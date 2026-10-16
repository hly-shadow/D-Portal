
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import CardWidget, SingleDirectionScrollArea

from app.models.data_model import ShelfItem
from app.views.components.item_widget import ShelfItemWidget

class MiddleComponent(CardWidget):
    item_drag_signal = Signal(object, QPoint)
    delete_signal = Signal(object)
    selection_changed_signal = Signal(object,bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8,8,8,8)

        self.scroll_area = SingleDirectionScrollArea(self)
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

        main_layout.addWidget(self.scroll_area)

    def remove_item_widget(self, item):
        for i in range(self.item_layout.count()):
            layout_item = self.item_layout.itemAt(i)
            if layout_item and layout_item.widget():
                widget = layout_item.widget()
                if item.get_unique_key() == widget.item.get_unique_key():
                    self.item_layout.removeWidget(widget)
                    widget.deleteLater()
                    break

    def add_item_widget(self,items: list):
        self.setUpdatesEnabled(False)
        try:
            for data in items:
                item_card = ShelfItemWidget(data)
                # ==================== 【关键绑定】 ====================
                # 当子组件被点击删除时, 直接交由控制器处理
                item_card.delete_signal.connect(lambda temp=data:self.delete_signal.emit(temp))

                item_card.selection_signal.connect(
                    lambda payload, d=data: self.selection_changed_signal.emit(d, payload[1])
                )

                item_card.item_drag_signal.connect(
                    lambda item, pos, d=data: self.item_drag_signal.emit(d,pos)
                )
                # 计算插入位置（始终在底部弹簧 Stretch 的上方）
                index = self.item_layout.count() - 1
                self.item_layout.insertWidget(index, item_card)
        finally:
            self.setUpdatesEnabled(True)