#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""D-Portal 主视图, 只负责界面和转发用户操作, 不创建 Model/Controller."""
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainterPath, QPainter, QBitmap
from PySide6.QtWidgets import QApplication, QVBoxLayout
from qframelesswindow import AcrylicWindow

from app.components.event_filter import MainWindowEventFilter
from app.components.edge_dock_manager import EdgeAutoDockManager, DockEdge
from app.views.components.bottom_widget import FooterComponent
from app.views.components.middle_widget import MiddleComponent
from app.views.components.top_widget import TopComponent

from app.config import APP_NAME, SHELF_WIDTH, SHELF_HEIGHT

class ShelfWindow(AcrylicWindow):
    item_delete_requested = Signal(object)
    item_selection_requested = Signal(object, bool)
    item_drag_requested = Signal(object, QPoint)
    close_requested = Signal()
    external_drop_requested = Signal(object)
    window_drag_started = Signal(QPoint)
    window_drag_moved = Signal(object)
    window_drag_ended = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.top_component = TopComponent(parent=self)
        self.middle_component = MiddleComponent(parent=self)
        self.footer_component = FooterComponent(parent=self)

        self.top_component.close_requested.connect(self.close_requested)
        self.middle_component.delete_signal.connect(self.item_delete_requested)
        self.middle_component.selection_changed_signal.connect(self.item_selection_requested)
        self.middle_component.item_drag_signal.connect(self.item_drag_requested)

        # 初始化管理器
        self.dock_manager = EdgeAutoDockManager(self, trigger_margin=15, hide_margin=5)
        self.event_filter = MainWindowEventFilter(self)
        self.installEventFilter(self.event_filter)
        self.event_filter.window_drag_started.connect(self.window_drag_started)
        self.event_filter.window_drag_moved.connect(self.window_drag_moved)
        self.event_filter.window_drag_ended.connect(self.window_drag_ended)
        self.event_filter.external_drop_requested.connect(self.external_drop_requested)
        # 关键：监听系统的调色板变化信号（当用户在系统设置里切深色/浅色时, 自动触发）
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.paletteChanged.connect(self.on_palette_changed)

        self._init_window()
        self._init_ui()
        self.apply_theme_style()

    def _init_window(self):
        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.titleBar.hide()

        screen = QApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            self.dock_manager.set_dock_edge(DockEdge.RIGHT)
            initial_x = geometry.right()
            initial_y = geometry.top() + (geometry.height() - SHELF_HEIGHT) // 2
            self.setGeometry(initial_x, initial_y, SHELF_WIDTH, SHELF_HEIGHT)
        self.setFixedSize(SHELF_WIDTH, SHELF_HEIGHT)
        self._apply_window_mask()
        self.setAcceptDrops(True)  # 允许接收外部拖入
        # 关闭原生 Acrylic 背景，使用 Qt 自定义配色
        self._disable_acrylic_background()

    def _init_ui(self):
        """主窗口布局组装：加载顶、中、底各个组件"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)
        # 1.加载顶部组件
        main_layout.addWidget(self.top_component)
        # 2.加载中间滚动区域组件
        main_layout.addWidget(self.middle_component, 1)
        # 3.加载底部卡片组件
        main_layout.addWidget(self.footer_component)

    # Controller 可调用的公开视图 API，不暴露内部子组件给业务层。
    def add_items(self, items: list):
        self.middle_component.add_item_widget(items)


    def remove_item(self, item):
        self.middle_component.remove_item_widget(item)


    def set_item_count(self, count: int):
        self.footer_component.update_count(count)


    def clear_selection(self):
        self.middle_component.clear_selection()

    def apply_theme_style(self):
        # 只设置主窗口属性，背景由 paintEvent 负责绘制
        self.setObjectName("ShelfWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.middle_component.apply_theme_style()
        self.top_component.apply_theme_style()
        self.footer_component.apply_theme_style()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QColor, QPainterPath
        from app.views.theme import get_theme_colors

        colors = get_theme_colors()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制不透明背景和圆角边框
        rect = self.rect().adjusted(0, 0, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 16, 16)

        # painter.fillPath(path, QColor(colors["window_bg"]))
        # painter.setPen(QPen(QColor(colors["panel_border"]), 1))
        # painter.drawPath(path)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, QColor(colors["window_bg"]))
        painter.end()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._apply_window_mask()

    def _disable_acrylic_background(self):
        """关闭原生背景效果和窗口阴影。"""
        hwnd = self.winId()

        try:
            self.windowEffect.removeBackgroundEffect(hwnd)
        except (AttributeError, RuntimeError) as exc:
            print(f"关闭原生背景效果失败: {exc}")

        try:
            self.windowEffect.removeShadowEffect(hwnd)
        except (AttributeError, RuntimeError) as exc:
            print(f"关闭原生窗口阴影失败: {exc}")

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )
    def on_palette_changed(self, _palette):
        self.apply_theme_style()


    def _apply_window_mask(self):
        path = QPainterPath()
        path.addRoundedRect(
            self.rect(),
            16,
            16,
        )

        mask = QBitmap(self.size())
        mask.fill(Qt.GlobalColor.color0)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, Qt.GlobalColor.color1)
        painter.end()

        self.setMask(mask)