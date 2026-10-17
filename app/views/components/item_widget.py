from typing import override

from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint, QFileInfo, Signal
from PySide6.QtWidgets import QSizePolicy, QHBoxLayout, QLabel, QFileIconProvider
from qfluentwidgets import TransparentToolButton, FluentIcon, CardWidget

from app.models.data_model import ShelfItem
from app.views.components.common_widget import ElidedLabel

class ShelfItemWidget(CardWidget):
    delete_signal = Signal(object)
    selection_signal = Signal(object)
    item_drag_signal = Signal(object, QPoint)

    def __init__(self, item: ShelfItem, parent= None):
        super().__init__(parent)
        self.item = item
        self.is_selected = False
        self._press_pos = None
        self.setFixedHeight(65)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12,8,12,8)
        main_layout.setSpacing(12)

        icon_label = QLabel(self)
        icon_label.setFixedSize(40,48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 获取系统原生图标
        provider = QFileIconProvider()
        file_path = QFileInfo(self.item.path)
        icon = provider.icon(file_path)
        icon_label.setPixmap(icon.pixmap(32,32))

        # 中间: 文件名(支持省略过长的文件名)
        name_label = ElidedLabel(self.item.name)

        delete_btn = TransparentToolButton()
        delete_btn.setIcon(FluentIcon.DELETE)
        delete_btn.setFixedSize(28, 28)
        delete_btn.clicked.connect(lambda :self.delete_signal.emit(self.item))

        main_layout.addWidget(icon_label)
        main_layout.addWidget(name_label, 1)
        main_layout.addWidget(delete_btn)

    @override
    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self.is_selected = not self.is_selected
            self._update_style()
            self.toggle_selection()
            e.accept()
        elif e.button() == Qt.MouseButton.LeftButton:
            self._press_pos = e.globalPosition().toPoint()
        super().mousePressEvent(e)

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

    def toggle_selection(self):
        # 将当前数据和最新的选中状态一起通过信号发射出去
        self.selection_signal.emit((self.item, self.is_selected))

    def _update_style(self):
        """根据 is_selected 的状态改变卡片样式"""
        if self.is_selected: # 选中状态
            style = """
                ShelfItemWidget {
                    background-color: rgba(0, 120, 212, 15%);
                    border: 2px solid #0078D4;
                    border-radius: 8px;
                }
            """
        else:
            style = """
                ShelfItemWidget {
                    background-color: #F9F9F9;
                    border: 1px solid #E1E1E1;
                    border-radius: 8px;
                }
                ShelfItemWidget:hover {
                    background-color: #F3F3F3;
                    border: 1px solid #C7C7C7;
                }
            """
        self.setStyleSheet(style)