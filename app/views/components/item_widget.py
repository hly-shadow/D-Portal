#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import override

from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint, QFileInfo, Signal
from PySide6.QtWidgets import QSizePolicy, QHBoxLayout, QLabel, QFileIconProvider
from qfluentwidgets import TransparentToolButton, FluentIcon, CardWidget

from app.models.data_model import ShelfItem
from app.views.theme import get_theme_colors
from app.views.components.common_widget import ElidedLabel

class ShelfItemWidget(CardWidget):
    delete_signal = Signal(object)
    selection_signal = Signal(object, bool)
    item_drag_signal = Signal(object, QPoint)

    def __init__(self, item: ShelfItem, parent= None):
        super().__init__(parent)
        self.item = item
        self.is_selected = False
        self.is_hovered = False
        self._press_pos = None
        self.setFixedHeight(65)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._init_ui()
        self.update_style()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12,8,12,8)
        main_layout.setSpacing(12)

        icon_label = QLabel(self)
        icon_label.setFixedSize(40,48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 获取系统原生图标
        provider = QFileIconProvider()
        if self.item.path:
            icon = provider.icon(QFileInfo(self.item.path))
        else:
            icon = provider.icon(QFileIconProvider.IconType.File)
        icon_label.setPixmap(icon.pixmap(32,32))

        # 中间: 文件名(支持省略过长的文件名)
        self.name_label = ElidedLabel(self.item.name)
        self.name_label.setObjectName("ShelfItemNameLabel")

        delete_btn = TransparentToolButton()
        delete_btn.setIcon(FluentIcon.DELETE)
        delete_btn.setFixedSize(28, 28)
        delete_btn.clicked.connect(lambda :self.delete_signal.emit(self.item))

        main_layout.addWidget(icon_label)
        main_layout.addWidget(self.name_label, 1)
        main_layout.addWidget(delete_btn)

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

        drag_threshold = 15
        if self._press_pos is not None:
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
        self.update_style()
        if emit_signal:
            self.selection_signal.emit(self.item, self.is_selected)

    def update_style(self):
        colors = get_theme_colors()
        if self.is_selected:
            bg = colors["selected_bg"]
            border = colors["selected_border"]
        elif self.is_hovered:
            bg = colors["card_hover_bg"]
            border = colors["selected_border"]
        else:
            # 支持鼠标悬浮判断 (可在 enterEvent/leaveEvent 中切换状态)
            bg = colors["card_bg"]
            border = colors["card_border"]

        text_color = colors["text_color"]
        font_family = colors["font_family"]

        self.setStyleSheet(f"""
            ShelfItemWidget {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
            ShelfItemWidget #ShelfItemNameLabel {{
                color: {text_color};
                font-family: {font_family};
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }}
        """)
    @override
    def enterEvent(self, e):
        super().enterEvent(e)
        self.is_hovered = True
        self.update_style()
        e.accept()
    @override
    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.is_hovered = False
        self.update_style()
        e.accept()