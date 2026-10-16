import os
from pathlib import Path
from PySide6.QtCore import Qt, QPoint, QMimeData, QUrl, QFileInfo
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QApplication

from app.models.shelf_manager import ShelfManager
from app.models.data_model import ShelfItem, ItemType
from app.views.shelf_window import ShelfWindow

class ShelfController:
    def __init__(self, shelf_manager: ShelfManager, window: ShelfWindow):
        self.shelf_manager = shelf_manager
        self.window = window
        self._drag_pos = None
        # 统一由控制器维护全局选中状态（存储唯一 Key）
        self._selected = set()
        # 绑定来自视图层的信号
        self.window.item_delete_requested.connect(self.handle_item_delete)
        self.window.select_requested.connect(self.handle_item_selection_changed)
        self.window.top_component.close_requested.connect(self.handle_window_close)


    def handle_incoming_data(self, mime_data):
        items = []
        if not mime_data:
            return
        if mime_data.hasUrls():
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if not file_path:
                    continue
                file_info = QFileInfo(file_path)
                file_name = Path(file_path).name
                if file_info.isDir():
                    item_type=ItemType.DIRECTORY
                elif file_info.isFile():
                    item_type=ItemType.FILE
                item = ShelfItem(
                    name=file_name,
                    path=file_path,
                    item_type=item_type
                )
                items.append(item)
                print(item.get_unique_key())
        if items:
            res = self.shelf_manager.add_item_filter(items)
            if res:
                self.window.render_items(res)
                self.window.update_count(self.shelf_manager.count())
        else:
            print("其它类型在开发中...")

    def handle_item_add(self, event):
        mime_data = event.mimeData()
        self.handle_incoming_data(mime_data)

    def handle_window_close(self):
        QApplication.quit()

    def handle_item_delete(self, item: ShelfItem):
        if item:
            self.shelf_manager.remove_item(item)
            self.window.remove_item_widget_by_data(item)
            self.window.update_count(self.shelf_manager.count())

    def handle_item_selection_changed(self, item: ShelfItem, is_selected: bool):
        """处理子组件传过来的选中/取消选中请求"""
        if is_selected:
            self._selected.add(item)
        else:
            self._selected.discard(item)

        print(len(self._selected))

    def handle_drag_start(self, pos: QPoint):
        # 记录鼠标点击位置相对窗口左上角的偏移, 防止窗口发生“瞬移”
        self._drag_pos = pos - self.window.frameGeometry().topLeft()

    def handle_drag_move(self, event):
        pos = event.globalPosition().toPoint()
        if self._drag_pos is not None:
            # 计算窗口应该移动到的新位置
            new_pos = pos - self._drag_pos
            self.window.move(new_pos)
            # 【核心逻辑】拖拽过程中实时检测是否需要吸附
            screen = QApplication.screenAt(event.globalPosition().toPoint()) or QApplication.primaryScreen()
            screen_geo = screen.availableGeometry()
            win_geo = self.window.geometry()
            # 调用管理器获取当前应该处于哪个边缘状态
            dock_manager = getattr(self.window, 'dock_manager', None)
            if dock_manager:
                target_edge = dock_manager.check_edge_during_drag(screen_geo, win_geo)
                dock_manager.set_dock_edge(target_edge)

    def handle_item_drag_out(self, dragged_item, pos):
        """
            dragged_item: 当前被鼠标按住并触发拖拽的那个卡片所对应的数据
            pos: 触发时的坐标
            """
        files_to_drag = []
        # 场景判断：
        # 如果当前拖拽的这个项，本身就在你的多选集合里，且多选集合数量 > 1
        if dragged_item in self._selected and len(self._selected) > 1:
            # 打包所有被选中的文件
            files_to_drag = list(self._selected)
        else:
            # 否则，只单独拖拽当前这一个文件
            files_to_drag = [dragged_item]

        # --- 开始执行 Qt 的标准外发拖拽 (QDrag) ---
        drag = QDrag(self.window)
        mime_data = QMimeData()

        # 将所有文件的路径转换为 QUrl 列表
        url_list = []
        for item in files_to_drag:
            file_path = item.path
            url_list.append(QUrl.fromLocalFile(file_path))

        mime_data.setUrls(url_list)
        drag.setMimeData(mime_data)

        # 执行拖拽动作（通常是复制动作 CopyAction）
        drop_action = drag.exec(Qt.DropAction.CopyAction, Qt.DropAction.CopyAction)
        # 2. 判断拖拽是否成功完成（只要不是忽略/取消，就代表投递成功）
        if drop_action != Qt.DropAction.IgnoreAction:
            files_to_remove = []
            if dragged_item in self._selected and len(self._selected) > 1:
                files_to_remove = list(self._selected)
            else:
                files_to_remove = [dragged_item]
            # 3. 遍历调用 shelf_manager 删除底层数据，并通知视图层移除对应卡片
            for item in files_to_remove:
                # 假设你的 shelf_manager 有删除数据的方法
                self.shelf_manager.remove_item(item)

                # 通知视图层（MiddleComponent）销毁对应的 UI 卡片
                self.window.middle_component.remove_item_widget(item)

            # 4. 如果你用了多选集合，删除后顺便清空多选状态
            self._selected.clear()

    def handle_drag_end(self):
        # 清除拖拽偏移状态
        self._drag_pos = None
