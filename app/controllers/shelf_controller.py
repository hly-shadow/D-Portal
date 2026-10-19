#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""协调 ShelfManager 与视图；不访问视图内部子控件。"""

from pathlib import Path
from PySide6.QtCore import Qt, QPoint, QMimeData, QUrl, QFileInfo
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QApplication

from app.models.shelf_manager import ShelfManager
from app.models.data_model import ShelfItem, ItemType


class ShelfController:
    def __init__(self, shelf_manager: ShelfManager, view):
        self._manager = shelf_manager
        self._view = view
        self._drag_offset = None
        # 用稳定的唯一键维护选择状态, 不保存模型对象本身.
        self._selected_keys: set[str] = set()
        self._connect_view()

    def _connect_view(self):
        """应用层传入的 view 只需提供这些公开信号."""
        self._view.item_delete_requested.connect(self.handle_item_delete)
        self._view.item_selection_requested.connect(self.handle_item_selection_changed)
        self._view.item_drag_requested.connect(self.handle_item_drag_out)
        self._view.close_requested.connect(self.handle_window_close)
        self._view.window_drag_started.connect(self.handle_drag_start)
        self._view.window_drag_moved.connect(self.handle_drag_move)
        self._view.window_drag_ended.connect(self.handle_drag_end)
        self._view.external_drop_requested.connect(self.handle_incoming_data)


    @staticmethod
    def handle_window_close():
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def handle_incoming_data(self, mime_data):
        """只接收存在的本地文件/目录: 一次批量操作只刷新一次视图."""
        if mime_data is None or not mime_data.hasUrls():
            return
        incoming: list[ShelfItem] = []
        for url in mime_data.urls():
            if not url.isLocalFile():
                continue
            raw_path = url.toLocalFile()
            if not raw_path:
                continue
            info = QFileInfo(raw_path)
            if info.isDir():
                item_type = ItemType.DIRECTORY
            elif info.isFile():
                item_type = ItemType.FILE
            else:
                # 避免把不存在或无法识别的路径作为 UNKNOWN 卡片加入。
                continue
            incoming.append(ShelfItem(
                name=Path(raw_path).name or raw_path,
                path=info.absoluteFilePath(),
                item_type=item_type,
            ))

        if not incoming:
            return
        added = self._manager.add_item_filter(incoming)
        if added:
            self._view.add_items(added)
            self._view.set_item_count(self._manager.count())
        else:
            print("其它类型在开发中...")

    def handle_item_delete(self, item: ShelfItem):
        if not item:
            return

        key = item.get_unique_key()
        if self._manager.remove_item(key):
            self._selected_keys.discard(key)
            self._view.remove_item(item)
            self._view.set_item_count(self._manager.count())

    def handle_item_selection_changed(self, item: ShelfItem, is_selected: bool):
        if not item:
            return
        key = item.get_unique_key()
        if not key:
            return
        if is_selected:
            self._selected_keys.add(key)
        else:
            self._selected_keys.discard(key)

    def handle_drag_start(self, global_pos: QPoint):
        self._drag_offset = global_pos - self._view.frameGeometry().topLeft()

    def handle_drag_move(self, event):
        if self._drag_offset is None:
            return
        global_pos = event.globalPosition().toPoint()
        self._view.move(global_pos - self._drag_offset)
        screen = QApplication.screenAt(global_pos) or QApplication.primaryScreen()
        if not screen:
            return
        dock_manager = self._view.dock_manager
        target_edge = dock_manager.check_edge_during_drag(
            screen.availableGeometry(), self._view.geometry()
        )
        dock_manager.set_dock_edge(target_edge)

    def handle_drag_end(self):
        self._drag_offset = None

    def handle_item_drag_out(self, dragged_item: ShelfItem, _pos: QPoint):
        if dragged_item is None or not dragged_item.path:
            return

        dragged_key = dragged_item.get_unique_key()
        if dragged_key in self._selected_keys and len(self._selected_keys) > 1:
            selected = self._manager.get_items_by_keys(self._selected_keys)
            files_to_drag = [item for item in selected if item.path]
        else:
            files_to_drag = [dragged_item]

        if not files_to_drag:
            return

        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(item.path) for item in files_to_drag])
        drag = QDrag(self._view)
        drag.setMimeData(mime_data)
        action = drag.exec(Qt.DropAction.CopyAction, Qt.DropAction.CopyAction)

        # 仅 CopyAction 表示目标接受了本次拖放; Ignore/Move/Link 均不清理。
        if action != Qt.DropAction.CopyAction:
            return

        for item in files_to_drag:
            key = item.get_unique_key()
            if self._manager.remove_item(key):
                self._selected_keys.discard(key)
                self._view.remove_item(item)
        self._view.set_item_count(self._manager.count())

        # 如果剩余选择少于两个，多选拖出语义已结束，清空残留选择。
        if len(self._selected_keys) < 2:
            self._selected_keys.clear()
            self._view.clear_selection()
