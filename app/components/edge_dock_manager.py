from enum import Enum, auto

from PySide6.QtCore import QObject, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication

class DockEdge(Enum):
    NONE = auto()
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()

class EdgeAutoDockManager(QObject):
    def __init__(self, window, trigger_margin=20, hide_margin=5):
        """
        :param window: 要控制的主窗口实例
        :param trigger_margin: 热区厚度, 鼠标距离屏幕边缘多少像素时触发显示
        :param hide_margin: 隐藏时保留在屏幕内可见的像素宽度
        """
        super().__init__(window)
        self.window = window
        self.trigger_margin = trigger_margin
        self.hide_margin = hide_margin

        self.current_edge = DockEdge.RIGHT # 默认停靠在屏幕右侧
        self.is_hidden = False

        # 1. 初始化动画
        self.anim = QPropertyAnimation(self.window, b"geometry")
        self.anim.setDuration(250)  # 动画时长 250ms
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 2. 定时检测鼠标位置
        self.timer = QTimer(self)
        self.timer.setInterval(150)  # 每 150ms 检查一次
        self.timer.timeout.connect(self._check_mouse_and_state)
        self.timer.start()

    def set_dock_edge(self, edge: DockEdge):
        """外部拖拽吸附时，由主窗口调用以更新当前贴边方向"""
        self.current_edge = edge

    def _get_active_hot_zone(self, screen_geo, win_geo) -> QRect:
        """
        核心：根据当前贴边方向，动态计算【热区】的范围和长度
        这里采用“热区长度与窗口尺寸关联”的设计，也可以改成固定长度或整条边
        """
        if self.current_edge == DockEdge.RIGHT:
            return QRect(
                screen_geo.right() - self.trigger_margin + 1,
                win_geo.y(),  # 热区起始位置跟随窗口的 Y 坐标
                self.trigger_margin,
                win_geo.height()  # 热区长度等于窗口高度
            )
        elif self.current_edge == DockEdge.LEFT:
            return QRect(
                screen_geo.left(),
                win_geo.y(),
                self.trigger_margin,
                win_geo.height()
            )
        elif self.current_edge == DockEdge.TOP:
            return QRect(
                win_geo.x(),  # 热区起始位置跟随窗口的 X 坐标
                screen_geo.top(),
                win_geo.width(),  # 热区长度等于窗口宽度
                self.trigger_margin
            )
        return QRect()

    def hide_window(self, screen_geo):
        if self.current_edge == DockEdge.NONE:
            return
        self.is_hidden = True
        win_geo = self.window.geometry()

        # 根据不同方向计算隐藏的目标几何位置
        if self.current_edge == DockEdge.RIGHT:
            target_x = screen_geo.right() - self.hide_margin
            target_rect = QRect(target_x, win_geo.y(), win_geo.width(), win_geo.height())
        elif self.current_edge == DockEdge.LEFT:
            target_x = screen_geo.left() - win_geo.width() + self.hide_margin
            target_rect = QRect(target_x, win_geo.y(), win_geo.width(), win_geo.height())
        elif self.current_edge == DockEdge.TOP:
            target_y = screen_geo.top() - win_geo.height() + self.hide_margin
            target_rect = QRect(win_geo.x(), target_y, win_geo.width(), win_geo.height())
        else:
            return

        self._start_animation(win_geo, target_rect)

    def show_window(self, screen_geo):
        self.is_hidden = False
        win_geo = self.window.geometry()

        # 根据不同方向计算呼出的目标几何位置
        if self.current_edge == DockEdge.RIGHT:
            target_x = screen_geo.right() - win_geo.width()
            target_rect = QRect(target_x, win_geo.y(), win_geo.width(), win_geo.height())
        elif self.current_edge == DockEdge.LEFT:
            target_x = screen_geo.left()
            target_rect = QRect(target_x, win_geo.y(), win_geo.width(), win_geo.height())
        elif self.current_edge == DockEdge.TOP:
            target_y = screen_geo.top()
            target_rect = QRect(win_geo.x(), target_y, win_geo.width(), win_geo.height())
        else:
            return

        self._start_animation(win_geo, target_rect)

    def _start_animation(self, start_rect, end_rect):
        self.anim.stop()
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)
        self.anim.start()


    def _check_mouse_and_state(self):
        if self.anim.state() == QPropertyAnimation.State.Running:
            return
        if self.current_edge == DockEdge.NONE:
            return

        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos) or QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()

        win_geo = self.window.geometry()
        hot_zone = self._get_active_hot_zone(screen_geo, win_geo)

        is_mouse_in_hot_zone = hot_zone.contains(cursor_pos)
        is_mouse_in_window = win_geo.contains(cursor_pos)


        if self.is_hidden:
            # ==================== 状态 A：隐藏时，检测是否需要呼出 ====================
            if is_mouse_in_hot_zone:
                self.show_window(screen_geo)
        else:
            # ==================== 状态 B：显示时，检测是否需要隐藏 ====================

            # 核心逻辑：只有当鼠标既不在窗口内，又不在边缘热区时(即真正移开屏幕边缘了),才执行隐藏
            if not is_mouse_in_window and not is_mouse_in_hot_zone:
                self.hide_window(screen_geo)

    def check_edge_during_drag(self, screen_geo, win_geo) -> DockEdge:
        """
        在拖拽过程中检测是否靠近屏幕边缘, 并返回对应的吸附方向
        snap_threshold: 触发吸附的像素阈值
        """
        snap_threshold = 15
        # 1. 检测左侧吸附
        if abs(win_geo.left() - screen_geo.left()) <= snap_threshold:
            return DockEdge.LEFT
        # 2. 检测顶部吸附
        elif abs(win_geo.top() - screen_geo.top()) <= snap_threshold:
            return DockEdge.TOP
        # 3. 检测右侧吸附
        elif abs(win_geo.right() - screen_geo.right()) <= snap_threshold:
            return DockEdge.RIGHT
        else:
            # 如果没有靠近任何边缘, 解除吸附状态, 变成自由悬浮窗
            return DockEdge.NONE