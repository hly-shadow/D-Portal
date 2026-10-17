#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用基础组件
"""
from typing import override, Tuple
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout
from qfluentwidgets import CardWidget


class DraggableCardWidget(CardWidget):
    """支持拖拽宿主窗口移动的通用卡片容器(支持自定义布局方向)"""
    def __init__(
            self,
            orientation: Qt.Orientation = Qt.Orientation.Horizontal,
            margins: Tuple[int, int, int, int] = (12,10,12,10),
            spacing: int = 8,
            parent=None
    ):
        super().__init__(parent)
        self._drag_pos = None

        # 根据传入的方向参数动态创建水平/垂直布局
        if orientation == Qt.Orientation.Horizontal:
            self.layout_box: QHBoxLayout | QVBoxLayout = QHBoxLayout(self)
        else:
            self.layout_box = QVBoxLayout(self)

        self.layout_box.setContentsMargins(*margins)
        self.layout_box.setSpacing(spacing)


class ElidedLabel(QLabel):
    """显示单行文本, 超过宽度时用省略号代替"""
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._full_text = text
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setMinimumWidth(20)
        self.setText(text)

    @override
    def setText(self, text: str):
        self._full_text = text
        self._update_elided_text()

    def _update_elided_text(self):
        metrics = QFontMetrics(self.font())
        width = self.width()
        if width > 0:
            elided = metrics.elidedText(
                self._full_text,
                Qt.TextElideMode.ElideMiddle,
                width
            )
            if self.text() != elided:
                super().setText(elided)

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided_text()
