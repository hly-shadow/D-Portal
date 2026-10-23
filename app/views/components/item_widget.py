#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import override

from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint, QFileInfo, Signal
from PySide6.QtWidgets import QSizePolicy, QHBoxLayout, QLabel, QFileIconProvider, QVBoxLayout, QWidget, QToolButton
from qfluentwidgets import TransparentToolButton, FluentIcon, CardWidget

from app.models.data_model import ShelfItem
from app.views.theme import get_theme_colors
from app.views.components.common_widget import ElidedLabel

class ShelfItemWidget(CardWidget):
    delete_signal = Signal(object)
    selection_signal = Signal(object, bool)
    item_drag_signal = Signal(object, QPoint)

    CARD_MIN_WIDTH = 100
    CARD_HEIGHT = 100
    
    def __init__(self, item: ShelfItem, parent= None):
        super().__init__(parent)
        self.item = item
        self.is_selected = False
        self.is_hovered = False
        self._press_pos = None
        self._theme_scheme = None
        self.setObjectName("ShelfItemWidget")
        self.setFixedSize(self.CARD_MIN_WIDTH, self.CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMouseTracking(True)
        self._init_ui()
        self.apply_theme_style()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8,8,8,8)
        root.setSpacing(5)
        # 文件预览/图标区域.使用系统原生文件图标.
        self.preview = QWidget(self)
        self.preview.setObjectName("ShelfItemPreview")
        self.preview.setFixedHeight(85)
        preview_layout = QVBoxLayout(self.preview)
        preview_layout.setContentsMargins(0,0,0,0)
        preview_layout.setSpacing(0)

        icon_row = QHBoxLayout()
        icon_row.setContentsMargins(0,0,0,0)
        icon_row.addStretch(1)
        self.icon_label = QLabel(self.preview)
        self.icon_label.setObjectName("ShelfItemIcon")
        self.icon_label.setFixedSize(48,48)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        provider = QFileIconProvider()
        if self.item.path:
            icon = provider.icon(QFileInfo(self.item.path))
        else:
            icon = provider.icon(QFileIconProvider.IconType.File)
        self.icon_label.setPixmap(icon.pixmap(44,44))
        icon_row.addWidget(self.icon_label)
        icon_row.addStretch(1)
        preview_layout.addStretch(1)
        preview_layout.addLayout(icon_row)
        preview_layout.addStretch(1)

        self.name_label = ElidedLabel(self.item.name, self)
        self.name_label.setObjectName("ShelfItemNameLabel")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setFixedHeight(22)
        # 操作按钮覆盖在卡片右上角,仅悬停/选中时显示,避免占用文件名空间.
        self.actions = QWidget(self)
        self.actions.setObjectName("ShelfItemActions")
        actions_layout = QHBoxLayout(self.actions)
        actions_layout.setContentsMargins(0,0,0,0)
        actions_layout.setSpacing(3)
        self.delete_btn = QToolButton(self.actions)
        self.delete_btn.setObjectName("ShelfItemDeleteButton")
        self.delete_btn.setIcon(FluentIcon.DELETE.icon())
        self.delete_btn.setToolTip("从 D-Portal 移除")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setFixedSize(26,26)
        self.delete_btn.clicked.connect(lambda: self.delete_signal.emit(self.item))
        actions_layout.addWidget(self.delete_btn)
        self.actions.adjustSize()
        self.actions.move(self.width() - self.actions.sizeHint().width() - 5, 5)
        self.actions.hide()

        root.addWidget(self.preview, 1)
        root.addWidget(self.name_label, 0)

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "actions"):
            self.actions.adjustSize()
            self.actions.move(self.width() - self.actions.sizeHint().width() - 5, 5)
        if hasattr(self, "name_label"):
            self.name_label._update_elided_text()

    @override
    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self.set_selected(not self.is_selected)
            e.accept()
        elif e.button() == Qt.MouseButton.LeftButton:
            self._press_pos = e.globalPosition().toPoint()
        super().mousePressEvent(e)

    @override
    def mouseReleaseEvent(self, e: QMouseEvent):
        self._press_pos = None
        super().mouseReleaseEvent(e)

    @override
    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if self._press_pos is not None:
            drag_threshold = 15
            # 检查移动距离是否超过系统规定的拖拽阈值
            if (event.globalPosition().toPoint() - self._press_pos).manhattanLength() > drag_threshold:
                # 达到阈值，在此处通过信号将拖拽意图发送出去
                self.item_drag_signal.emit(self.item, event.globalPosition().toPoint())
                self._press_pos = None  # 重置, 防止重复触发
            super().mouseMoveEvent(event)

    def set_selected(self, selected: bool, emit_signal: bool = True):
        if self.is_selected == selected:
            return
        self.is_selected = selected
        self.apply_theme_style()
        if emit_signal:
            self.selection_signal.emit(self.item, self.is_selected)

    def set_card_width(self, width:int):
        self.setFixedSize(width, self.CARD_HEIGHT)
        if hasattr(self, "actions"):
            self.actions.adjustSize()
            self.actions.move(self.width() - self.actions.width() - 5, 5)
        if hasattr(self, "name_label"):
            self.name_label._update_elided_text()

    @override
    def enterEvent(self, e):
        super().enterEvent(e)
        self.is_hovered = True
        self.apply_theme_style()
        e.accept()
    @override
    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.is_hovered = False
        self.apply_theme_style()
        e.accept()

    def apply_theme_style(self, scheme: str | None = None):
        if scheme is None:
            from app.views.theme import get_current_color_scheme
            scheme = get_current_color_scheme()
        self._theme_scheme = scheme
        colors = get_theme_colors(scheme)

        if self.is_selected:
            bg = colors["selected_bg"]
            border = colors["selected_border"]
            text_color = colors["selected_text"]
        elif self.is_hovered:
            bg = colors["card_hover_bg"]
            border = colors["selected_border"]
            text_color = colors["text_color"]
        else:
            bg = colors["card_bg"]
            border = colors["card_border"]
            text_color = colors["text_color"]

        self.setStyleSheet(f"""
            ShelfItemWidget {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {colors["card_radius"]};
            }}

            ShelfItemWidget QWidget#ShelfItemPreview {{
                background-color: {colors["preview_bg"]};
                border: none;
                border-radius: 7px;
            }}

            ShelfItemWidget QLabel#ShelfItemIcon,
            ShelfItemWidget QLabel#ShelfItemNameLabel {{
                background-color: transparent;
                border: none;
            }}

            ShelfItemWidget QLabel#ShelfItemNameLabel {{
                color: {text_color};
                font-family: {colors["font_family"]};
                font-size: 13px;
                font-weight: 600;
            }}

            QToolButton#ShelfItemDeleteButton {{
                background-color: {colors["panel_bg"]};
                color: {colors["text_color"]};
                border: 1px solid {colors["card_border"]};
                border-radius: 7px;
                padding: 3px;
            }}

            QToolButton#ShelfItemDeleteButton:hover {{
                background-color: {colors["danger_bg"]};
                color: {colors["danger_text"]};
                border-color: {colors["danger_text"]};
            }}

            QToolButton#ShelfItemDeleteButton:pressed {{
                background-color: {colors["danger_hover_bg"]};
                color: {colors["danger_text"]};
            }}
        """)

        if hasattr(self, "actions"):
            self.actions.setVisible(
                self.is_hovered or self.is_selected
            )
