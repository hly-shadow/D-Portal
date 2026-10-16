import os
from typing import override

from PySide6.QtCore import (
    Qt,
    Signal,
    QFileInfo,
    QUrl,
    QMimeData, QPoint
)
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QFileIconProvider, QSizePolicy, QApplication
)
from PySide6.QtGui import QDrag
# noinspection PyPep8Naming
from qfluentwidgets import TransparentToolButton, FluentIcon as FIF, CardWidget

from ..core.shelf_item import ShelfItem
from .widgets import ElidedLabel

class ShelfItemWidget(CardWidget):
    deleted_signal = Signal(object)
    selection_toggled = Signal(object)
    drag_finished = Signal(list, bool)

    def __init__(self, item: ShelfItem, parent= None):
        super().__init__(parent)
        self.item = item
        self.is_selected = False
        self.selected_items = [self.item]

        self.setObjectName("ShelfItem")
        self.drag_start_pos = QPoint() # 记录鼠标按下的位置
        self.setFixedHeight(65)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._init_ui()

    def _init_ui(self):

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12,8,12,8)
        layout.setSpacing(12)

        # 1. 左侧图标
        icon_label = QLabel()
        icon_label.setFixedSize(40,48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 获取系统原生图标
        provider = QFileIconProvider()
        file_path = QFileInfo(self.item.path)
        icon = provider.icon(file_path)
        icon_label.setPixmap(icon.pixmap(32,32))

        # 2. 中间: 文件名(支持省略过长的文件名)
        name_label = ElidedLabel(self.item.name)

        # 3. 右侧操作区: 锁定按钮 + 删除按钮
        lock_btn = TransparentToolButton()
        lock_btn.setIcon(FIF.CLOSE)
        lock_btn.setFixedSize(28, 28)
        lock_btn.clicked.connect(self._lock)

        delete_btn = TransparentToolButton()
        delete_btn.setIcon(FIF.DELETE)
        delete_btn.setFixedSize(28, 28)
        delete_btn.clicked.connect(self._delete)

        layout.addWidget(icon_label)
        layout.addWidget(name_label, 1)
        layout.addWidget(lock_btn)
        layout.addWidget(delete_btn)

    def _delete(self):
        self.deleted_signal.emit(self.item)

    def _lock(self):
        pass

    # ================ 核心：实现拖拽 (D-Portal -> 外部) ================
    @override
    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            # 【核心】右键点击：切换选中状态
            self.is_selected = not self.is_selected
            self.set_selected_style()
            e.accept()
        elif e.button() == Qt.LeftButton:
            self.drag_start_pos = e.pos()

        super().mousePressEvent(e)

    @override
    def mouseMoveEvent(self, event) -> None:
        # 确保按住鼠标并移动
        if not (event.buttons() & Qt.LeftButton):
            return
        # 检查移动距离是否超过系统默认的拖拽阈值（防止轻微抖动被误判为拖拽）
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        self._drag_file()



    def set_selected_style(self):
        """根据 is_selected 的状态动态改变卡片样式"""
        if self.is_selected:
            self.setStyleSheet("""
                ShelfItemWidget {
                    border: 2px solid #0078d4;
                    border-radius: 6px;
                    background-color: rgba(0, 120, 212, 0.08);
                }
            """)
        else:
            self.setStyleSheet('')

    def _drag_file(self):
        items = (
            list(self.selected_items)
            if self.is_selected
            else [self.item]
        )
        paths = []
        drag_items = []
        for item in items:
            path = os.path.abspath(item.path)
            if os.path.exists(path):
                paths.append(QUrl.fromLocalFile(path))
                drag_items.append(item)
        if not paths:
            return
        mime_data = QMimeData()
        mime_data.setUrls(paths)

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        result = drag.exec(Qt.DropAction.CopyAction, Qt.DropAction.CopyAction)

        flag = result == Qt.DropAction.CopyAction
        self.drag_finished.emit(drag_items, flag)
