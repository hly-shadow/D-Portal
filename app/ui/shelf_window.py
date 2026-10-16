import os.path
from pathlib import Path
from typing import override

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QFileInfo
from PySide6.QtGui import QCursor,QIcon
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QApplication, QFileIconProvider

# noinspection PyPep8Naming
from qfluentwidgets import (
    BodyLabel,
    SubtitleLabel,
    CaptionLabel,
    HorizontalSeparator,
    SingleDirectionScrollArea,
    FluentIcon as FIF,
    TransparentToolButton, CardWidget,
    IconWidget
)
from qfluentwidgets.components.widgets import icon_widget
from qframelesswindow import AcrylicWindow

from ..config import (
    APP_NAME,
    SHELF_WIDTH,
    SHELF_HEIGHT,
    ICON_PATH
)
from ..core.shelf_item import ItemType, ShelfItem

from ..core.shelf_manager import ShelfManager
from .shelf_item_widget import ShelfItemWidget
from .widgets import DraggableCardWidget

class ShelfWindow(AcrylicWindow):
    def __init__(self, shelf_manager: ShelfManager, parent=None):
        super().__init__(parent)
        self.scroll_area = None
        self.item_container = None
        self.item_layout = None
        self.count_label = None
        self.shelf_manager = shelf_manager

        self._selected_paths = set()
        self._item_widgets = []

        # 边缘隐藏核心配置参数
        self.dock_edge = 'right'
        self.is_hidden = True # 当前是否处于隐藏状态
        self.visible_margin = 5 # 隐藏时留在屏幕边缘的像素宽度
        self.edge_threshold = 15 # 判断贴边的距离阈值(像素)

        self.edge_zone_width = 15

        # 初始化平滑动画对象(针对窗口的pos属性)
        self.animation = QPropertyAnimation(self, b"pos", self)
        self.animation.setDuration(250) # 动画时长 250 毫秒
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic) # 缓动曲线, 平滑自然


        # 定时器检测鼠标位置(用于自动隐藏与呼出)
        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(150)
        self.hide_timer.timeout.connect(self.check_mouse_position)
        self.hide_timer.start()
        self._init_window()
        self._init_ui()
        self.refresh_items()
        self.setMouseTracking(True)

    @override
    def closeEvent(self, event) -> None:
        if hasattr(self, 'hide_timer') and self.hide_timer.isActive():
            self.hide_timer.stop()
        QApplication.quit()
        super().closeEvent(event)

    def _init_window(self):
        self.setWindowTitle(APP_NAME)

        # 1. 必须开启 FramelessWindowHint 和透明背景（解决按钮无法响应和边框冲突）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.titleBar.hide()

        screen = QApplication.primaryScreen().availableGeometry()

        initial_x = screen.right() - self.visible_margin
        initial_y = screen.top() + (screen.height() - SHELF_HEIGHT) // 2

        self.setGeometry(initial_x, initial_y, SHELF_WIDTH, SHELF_HEIGHT)
        # 允许接收传入的文件
        self.setAcceptDrops(True)


    def _init_ui(self):
        # 主窗口布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10,10,10,10)
        main_layout.setSpacing(8)

        # ==================== 1. 顶部卡片 (Header Card) ====================
        icon_widget = IconWidget(ICON_PATH)
        top_card = DraggableCardWidget(icon_widget)
        top_layout = QHBoxLayout(top_card)
        top_layout.setContentsMargins(16,12,8,12)
        top_layout.setSpacing(4)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        top_layout.addWidget(icon_widget)
        title = SubtitleLabel(self)
        title.setText("D-Portal")
        title.setParent(top_card)

        subtitle = CaptionLabel(self)
        subtitle.setText("Shelf")
        subtitle.setParent(top_card)

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        # 1.2 右侧透明关闭按钮
        close_btn = TransparentToolButton(top_card)
        close_btn.setIcon(FIF.CLOSE)
        close_btn.setFixedSize(32,32)
        close_btn.clicked.connect(self.close) # 关闭窗口

        # 组装顶部卡片
        top_layout.addLayout(text_layout)
        top_layout.addStretch()
        top_layout.addWidget(close_btn,0,Qt.AlignmentFlag.AlignTop)

        # ==================== 2. 中间卡片 (Scroll Area Card) ====================
        middle_card = CardWidget()
        middle_layout = QVBoxLayout(middle_card)
        middle_layout.setContentsMargins(8,8,8,8)

        # 2.1 创建单向滚动区域
        self.scroll_area = SingleDirectionScrollArea(middle_card)
        self.scroll_area.setWidgetResizable(True)

        self.item_container = QWidget()
        self.item_layout = QVBoxLayout(self.item_container)
        self.item_layout.setContentsMargins(0,0,0,0)
        self.item_layout.setSpacing(8)
        self.item_layout.addStretch()

        self.scroll_area.setWidget(self.item_container)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        middle_layout.addWidget(self.scroll_area)

        # ==================== 3. 底部卡片 (Footer Card) ====================
        bottom_card = CardWidget(self)
        bottom_layout = QVBoxLayout(bottom_card)
        bottom_layout.setContentsMargins(16,12,16,12)
        bottom_layout.setSpacing(10)

        h_sep = HorizontalSeparator(bottom_card)
        self.count_label = BodyLabel(bottom_card)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        bottom_layout.addWidget(h_sep)
        bottom_layout.addWidget(self.count_label)

        # ==================== 4. 组装到主界面布局 ====================
        main_layout.addWidget(top_card)
        main_layout.addWidget(middle_card, 1)
        main_layout.addWidget(bottom_card)


    def refresh_items(self):
        # 删除旧的卡片，但保留最后的 Stretch
        while self.item_layout.count() > 1:
            layout_item = self.item_layout.takeAt(0)
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()

        self._item_widgets.clear()
        # 创建卡片并连接移除信号
        for shelf_item in self.shelf_manager.items:
            widget = ShelfItemWidget(shelf_item)

            path_key = os.path.normcase(
                os.path.abspath(shelf_item.path)
            )
            self._selected_paths.add(path_key)

            widget.deleted_signal.connect(
                self._remove_item
            )
            widget.selection_toggled.connect(
                self._toggle_selection
            )
            widget.drag_finished.connect(
                self._on_drag_finished
            )

            self.item_layout.insertWidget(
                self.item_layout.count() - 1,
                widget,
            )

            self._item_widgets.append(widget)

        # 所有卡片共享当前选中列表
        selected_items = [
            item
            for item in self.shelf_manager.items
            if os.path.normcase(os.path.abspath(item.path))
               in self._selected_paths
        ]

        for widget in self._item_widgets:
            widget.selected_items = selected_items

        self._update_count()

    def _remove_item(self, item):
        print("remove_item triggered:", item)
        self.shelf_manager.remove_item(item)
        self.refresh_items()

    def _update_count(self):
        count = self.shelf_manager.count()
        self.count_label.setText(
            f"{count} item"
            if count == 1
            else f"{count} items"
        )

    # 轮询检测：当隐藏时，鼠标靠近边缘则展开
    def check_mouse_position(self):
        if self.animation.state() == QPropertyAnimation.State.Running:
            return
        global_mouse_pos = QCursor.pos()
        screen = QApplication.primaryScreen().availableGeometry()
        win_geo = self.geometry()
        # ==================== 1. 定义边缘热区范围 ====================
        # 根据当前的停靠边缘计算热区判定条件
        mouse_in_edge_zone = False
        if self.dock_edge == 'right':
            # 屏幕最右侧往左数 edge_zone_width 像素的区域，以及屏幕的高度范围内
            mouse_in_edge_zone = (
                    global_mouse_pos.x() >= screen.right() - self.edge_zone_width and
                    screen.top() <= global_mouse_pos.y() <= screen.bottom()
            )
        elif self.dock_edge == 'left':
            mouse_in_edge_zone = (
                    global_mouse_pos.x() <= screen.left() + self.edge_zone_width and
                    screen.top() <= global_mouse_pos.y() <= screen.bottom()
            )
        elif self.dock_edge == 'top':
            mouse_in_edge_zone = (
                    global_mouse_pos.y() <= screen.top() + self.edge_zone_width and
                    screen.left() <= global_mouse_pos.x() <= screen.right()
            )
        if self.is_hidden:
            # ==================== 状态 A：隐藏时，检测是否需要呼出 ====================
            if mouse_in_edge_zone:
                self.show_normal_state()
        else:
            # ==================== 状态 B：显示时，检测是否需要隐藏 ====================
            # 1. 鼠标是否在窗口内部
            mouse_in_window = win_geo.contains(global_mouse_pos)

            # 核心逻辑：只有当鼠标既不在窗口内，又不在边缘热区时（即真正移开屏幕边缘了），才执行隐藏
            if not mouse_in_window and not mouse_in_edge_zone:
                self.hide_to_edge()


    def start_animation(self, target_pos, hide: bool):
        self.animation.stop()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(target_pos)
        self.animation.start()
        self.is_hidden = hide

    def show_normal_state(self):
        screen = QApplication.primaryScreen().availableGeometry()
        win_geo = self.geometry()

        if self.dock_edge == 'left':
            target_pos = QPoint(screen.left(), win_geo.y())
        elif self.dock_edge == 'right':
            target_pos = QPoint(screen.right() - win_geo.width(), win_geo.y())
        elif self.dock_edge == 'top':
            target_pos = QPoint(win_geo.x(),screen.top())
        else:
            return
        self.start_animation(target_pos, hide=False)

    def hide_to_edge(self):
        if self.is_hidden:
            return
        screen = QApplication.primaryScreen().availableGeometry()
        win_geo = self.geometry()
        # 检测左边缘
        if abs(win_geo.left() - screen.left()) <= self.edge_threshold:
            self.dock_edge = 'left'
            target_pos = QPoint(screen.left() - win_geo.width() + self.visible_margin, win_geo.y())
            self.start_animation(target_pos, True)
        # 检测右边缘
        elif abs(win_geo.right() - screen.right()) <= self.edge_threshold:
            self.dock_edge = 'right'
            target_pos = QPoint(screen.right() - self.visible_margin, win_geo.y())
            self.start_animation(target_pos, hide=True)
        # 检测上边缘
        elif abs(win_geo.top() - screen.top()) <= self.edge_threshold:
            self.dock_edge = 'top'
            target_pos = QPoint(win_geo.x(), screen.top() - win_geo.height() + self.visible_margin)
            self.start_animation(target_pos, hide=True)

    def _toggle_selection(self, item):
        path_key = os.path.normcase(
            os.path.abspath(item.path)
        )

        if path_key in self._selected_paths:
            self._selected_paths.remove(path_key)
        else:
            self._selected_paths.add(path_key)

        self.refresh_items()
    def _on_drag_finished(self, items, res):
        if not res:
            return
        for item in items:
            self.shelf_manager.remove_item(item)
            self._selected_paths.discard(
                os.path.normcase(
                    os.path.abspath(item.path)
                )
            )
        self.refresh_items()
    @override
    def dragEnterEvent(self, event) -> None:
        mime_data = event.mimeData()

        if mime_data.hasUrls():
            local_files = [
                url.toLocalFile()
                for url in mime_data.urls()
                if url.isLocalFile() and url.toLocalFile()
            ]
            if local_files:
                event.setDropAction(Qt.DropAction.CopyAction)
                event.accept()
                return
        event.ignore()

    @override
    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    @override
    def dropEvent(self, event) -> None:
        mime_data = event.mimeData()

        if not mime_data.hasUrls():
            event.ignore()
            return

        icon_provider = QFileIconProvider()
        # 1. 检查是否包含 URL（文件、文件夹或网页链接）
        if mime_data.hasUrls():
            for url in mime_data.urls():
                # 本地文件
                if url.isLocalFile():

                    full_path = url.toLocalFile()
                    if not full_path:
                        continue

                    file_info = QFileInfo(full_path)
                    file_name = Path(full_path).name
                    file_icon: QIcon = icon_provider.icon(file_info)

                    if file_info.isDir():
                        item_type = ItemType.DIRECTORY
                    else:
                        item_type = ItemType.FILE

                    item = ShelfItem(
                        name=file_name,
                        path=full_path,
                        icon=file_icon,
                        item_type=item_type
                    )
                    self.shelf_manager.add_item(item)
                    self.refresh_items()
                    # 声明拖放为复制语义：源文件不会被移动
                    event.setDropAction(Qt.DropAction.CopyAction)
                    event.accept()
                else:
                    url_str = url.toString()
                    item = ShelfItem(
                        name=url_str,
                        url=url_str,
                        item_type=ItemType.URL
                    )
                    self.shelf_manager.add_item(item)
                    self.refresh_items()
                    # 声明拖放为复制语义：源文件不会被移动
                    event.setDropAction(Qt.DropAction.CopyAction)
                    event.accept()
        # 2. 检查是否为纯文本拖入
        elif mime_data.hasText():
            pass