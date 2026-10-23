#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from qfluentwidgets import CardWidget, BodyLabel

from app.views.theme import get_theme_colors


class FooterComponent(CardWidget):
    """底部轻量状态栏，暂时仅显示当前暂存条目数量."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FooterComponent")
        self.setFixedHeight(32)
        self._init_ui()
        self.apply_theme_style()

    def _init_ui(self):
        # 设置内部布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)
        self.count_label = BodyLabel(self)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # 组装布局
        layout.addWidget(self.count_label)
        # 默认初始显示 0 items
        self.update_count(0)

    def update_count(self, count: int):
        """对外暴露的方法：用于更新统计数量"""
        text = f"{count} item" if count == 1 else f"{count} items"
        self.count_label.setText(text)

    def apply_theme_style(self, scheme: str | None = None):
        colors = get_theme_colors(scheme)

        self.setStyleSheet(f"""
            FooterComponent {{
                background-color: {colors["panel_bg"]};
                border: 1px solid {colors["panel_border"]};
                border-radius: {colors["radius"]};
            }}

            FooterComponent QLabel {{
                color: {colors["sub_text_color"]};
                background: transparent;
                border: none;
                font-size: 12px;
            }}
        """)
