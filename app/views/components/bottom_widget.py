#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout
from qfluentwidgets import CardWidget, BodyLabel

from app.views.theme import get_theme_colors


class FooterComponent(CardWidget):
    """展示底部分割线与数量统计的自定义组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.count_label = None
        self._init_ui()

    def _init_ui(self):
        # 设置内部布局
        bottom_layout = QVBoxLayout(self)
        bottom_layout.setContentsMargins(10, 5, 10, 5)
        bottom_layout.setSpacing(10)

        self.count_label = BodyLabel(self)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # 组装布局
        bottom_layout.addWidget(self.count_label)

        # 默认初始显示 0 items
        self.update_count(0)

    def update_count(self, count: int):
        """对外暴露的方法：用于更新统计数量"""
        text = f"{count} item" if count == 1 else f"{count} items"
        self.count_label.setText(text)

    def apply_theme_style(self):
        colors = get_theme_colors()
        self.setStyleSheet(f"""
            FooterComponent {{
                background-color: {colors["panel_bg"]};
                border: 1px solid {colors["panel_border"]};
                border-radius: {colors["radius"]};
            }}
        """)