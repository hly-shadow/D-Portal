#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import override

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QVBoxLayout, QWidget, QFrame, QSizePolicy, QGridLayout
from qfluentwidgets import CardWidget, SingleDirectionScrollArea

from app.models.data_model import ShelfItem
from app.views.components.item_widget import ShelfItemWidget
from app.views.theme import get_theme_colors


class MiddleComponent(CardWidget):
    item_drag_signal = Signal(object, QPoint)
    delete_signal = Signal(object)
    selection_changed_signal = Signal(object,bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_widgets = {}
        self._init_ui()
        self.apply_theme_style()

    def _init_ui(self):
        self.setObjectName("MiddleComponent")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8,8,8,8)
        main_layout.setSpacing(0)

        self.scroll_area = SingleDirectionScrollArea(self)
        self.scroll_area.setObjectName("ShelfScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.item_container = QWidget()
        self.item_container.setObjectName("ShelfGridContainer")
        self.item_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.item_layout = QGridLayout(self.item_container)
        self.item_layout.setContentsMargins(4,4,8,8)
        self.item_layout.setHorizontalSpacing(10)
        self.item_layout.setVerticalSpacing(10)
        self.item_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.item_container)
        main_layout.addWidget(self.scroll_area)

    def _reflow_grid(self):
        """根据窗口宽度动态计算列数和卡片宽度."""
        if not hasattr(self, "item_layout"):
            return
        widgets = list(self._item_widgets.values())
        viewport_width = self.scroll_area.viewport().width()

        if viewport_width <= 0:
            return
        # 与 item_container 的左右内边距保持一致
        left_margin = 4
        right_margin = 8
        spacing = self.item_layout.horizontalSpacing()

        available_width = max(
            1,
            viewport_width - left_margin - right_margin,
        )
        min_card_width = ShelfItemWidget.CARD_MIN_WIDTH

        # 根据最小卡片宽度计算列数
        columns = max(
            1,
            (available_width + spacing)
            // (min_card_width + spacing),
        )
        # 平均分配宽度，消除右侧多余空白
        card_width = (
            available_width - spacing * (columns - 1)
        ) // columns
        # 缓存包含卡片数量，确保窗口宽度不变时新增卡片也会重新布局。
        layout_state = (viewport_width, columns, card_width, len(widgets))
        # 防止反复 resize 时无意义地重排
        if getattr(self, "_last_grid_width", None) == layout_state:
            return
        self._last_grid_state = layout_state
        self._last_grid_width = (
            viewport_width, columns, card_width
        )
        self.setUpdatesEnabled(False)
        try:
            for index, widget in enumerate(widgets):
                self.item_layout.removeWidget(widget)
                widget.set_card_width(card_width)
                row = index // columns
                column = index % columns
                self.item_layout.addWidget(
                    widget, row, column,
                    Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
                )
            # 容器至少与视口一样宽
            self.item_container.setMinimumWidth(viewport_width)
            self.item_container.adjustSize()
        finally:
            self.setUpdatesEnabled(True)
            self.item_container.update()

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reflow_grid()

    def remove_item_widget(self, item:ShelfItem):
        key = item.get_unique_key()
        widget = self._item_widgets.pop(key, None)
        if widget is not None:
            self.item_layout.removeWidget(widget)
            widget.deleteLater()
            self._reflow_grid()

    def add_item_widget(self,items: list[ShelfItem]):
        self.setUpdatesEnabled(False)
        try:
            for data in items:
                key = data.get_unique_key()
                if key in self._item_widgets:
                    continue
                item_card = ShelfItemWidget(data, self.item_container)
                # ==================== 【关键绑定】 ====================
                # 当子组件被点击删除时, 直接交由控制器处理
                item_card.delete_signal.connect(lambda temp=data:self.delete_signal.emit(temp))

                item_card.selection_signal.connect(
                    lambda item, selected, d=data: self.selection_changed_signal.emit(d, selected)
                )

                item_card.item_drag_signal.connect(
                    lambda item, pos, d=data: self.item_drag_signal.emit(d,pos)
                )
                self._item_widgets[key] = item_card
            self._reflow_grid()
        finally:
            self.setUpdatesEnabled(True)
            self.update()

    def clear_selection(self):
        for widget in self._item_widgets.values():
            widget.set_selected(False, emit_signal=False)

    def apply_theme_style(self, scheme: str | None = None):
        if scheme is None:
            from app.views.theme import get_current_color_scheme
            scheme = get_current_color_scheme()
        self._theme_scheme = scheme
        colors = get_theme_colors(scheme)

        self.setStyleSheet(f"""
            MiddleComponent {{
                background-color: {colors["middle_bg"]};
                border: 1px solid {colors["middle_border"]};
                border-radius: {colors["radius"]};
            }}

            QScrollArea#ShelfScrollArea {{
                background: transparent;
                border: none;
            }}

            QScrollArea#ShelfScrollArea QWidget#qt_scrollarea_viewport {{
                background-color: {colors["middle_bg"]};
                border: none;
            }}

            QWidget#ShelfGridContainer {{
                background-color: {colors["middle_bg"]};
                border: none;
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 4px 0 4px 0;
            }}

            QScrollBar::handle:vertical {{
                background: {colors["scrollbar"]};
                min-height: 28px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {colors["scrollbar_hover"]};
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

        for widget in self._item_widgets.values():
            widget.apply_theme_style(scheme)
