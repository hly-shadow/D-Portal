#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout

from qfluentwidgets import (
    SubtitleLabel,
    FluentIcon,
    TransparentToolButton,
    IconWidget
)

from app.views.components.common_widget import DraggableCardWidget
from app.config import ICON_PATH
from app.views.theme import get_theme_colors


class TopComponent(DraggableCardWidget):
    close_requested = Signal()

    def __init__(self, title: str = "D-Portal", parent=None):
        super().__init__(orientation=Qt.Orientation.Horizontal, margins=(12,10,12,10), spacing=6, parent=parent)
        self.title = title

        self._init_ui()

    def _init_ui(self):

        # 左侧图标
        icon_widget = IconWidget(ICON_PATH)
        icon_widget.setFixedSize(32, 32)

        # 中间文字区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        title = SubtitleLabel(self.title,self)
        text_layout.addWidget(title)


        # 右侧关闭按钮
        close_btn = TransparentToolButton(self)
        close_btn.setIcon(FluentIcon.CLOSE)
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.close_requested.emit)

        # 5. 组装到布局中
        self.layout_box.addWidget(icon_widget)
        self.layout_box.addLayout(text_layout)
        self.layout_box.addStretch(1)
        self.layout_box.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignTop)

    def apply_theme_style(self):
        colors = get_theme_colors()
        self.setStyleSheet(f"""
            TopComponent{{
                background-color: {colors["panel_bg"]};
                border: 1px solid {colors["panel_border"]};
                border-radius: {colors["radius"]};
            }}
        """)