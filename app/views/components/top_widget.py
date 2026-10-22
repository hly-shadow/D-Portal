#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, Signal

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
        self.setObjectName("TopComponent")
        self.setFixedHeight(54)
        self._init_ui()
        self.apply_theme_style()

    def _init_ui(self):
        # 左侧图标
        icon_widget = IconWidget(ICON_PATH, self)
        icon_widget.setFixedSize(30, 30)

        title = SubtitleLabel(self.title,self)
        title.setObjectName("AppTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 600; background: transparent; border: none;")

        # 右侧关闭按钮
        close_btn = TransparentToolButton(self)
        close_btn.setIcon(FluentIcon.CLOSE)
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close_requested.emit)

        # 5. 组装到布局中
        self.layout_box.addWidget(icon_widget, 0, Qt.AlignmentFlag.AlignVCenter)
        self.layout_box.addWidget(title, 0, Qt.AlignmentFlag.AlignVCenter)
        self.layout_box.addStretch(1)
        self.layout_box.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignVCenter)

    def apply_theme_style(self):
        colors = get_theme_colors()
        self.setStyleSheet(f"""
            TopComponent {{
                background-color: {colors['panel_bg']};
                border: 1px solid {colors['panel_border']};
                border-radius: 12px;
            }}
            TopComponent QToolButton {{
                background: transparent;
                border: none;
                border-radius: 7px;
                color: {colors['text_color']};
            }}
            TopComponent QToolButton:hover {{
                background-color: {('#FDECEC' if colors is not None and colors['text_color'] == '#20242B' else '#513238')};
                color: {('#C93737' if colors['text_color'] == '#20242B' else '#FFB4B4')};
            }}
        """)