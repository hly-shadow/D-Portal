import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QPoint, Qt, QUrl
from PySide6.QtWidgets import QApplication

from app.models.data_model import ShelfItem, ItemType
from app.controllers.shelf_controller import ShelfController


@pytest.fixture(scope="session")
def qapp():
    """确保整个测试会话中存在一个 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_shelf_manager():
    """Mock ShelfManager"""
    manager = MagicMock()
    manager.count.return_value = 0
    return manager


@pytest.fixture
def mock_window():
    """Mock ShelfWindow 及其关联组件"""
    window = MagicMock()
    # 模拟信号连接
    window.item_delete_requested = MagicMock()
    window.select_requested = MagicMock()
    window.top_component.close_requested = MagicMock()
    return window


@pytest.fixture
def controller(qapp, mock_shelf_manager, mock_window):
    """初始化 ShelfController 实例"""
    return ShelfController(mock_shelf_manager, mock_window)


def test_handle_incoming_data_urls(controller, mock_shelf_manager, mock_window):
    """测试处理传入的 URL 数据（文件/目录拖入）"""
    # 准备 MIME 数据
    mock_mime = MagicMock()
    mock_mime.hasUrls.return_value = True

    # 模拟 QUrl
    mock_url = MagicMock(spec=QUrl)
    # 假设拖入了一个虚拟路径
    mock_url.toLocalFile.return_value = "/path/to/test_file.txt"
    mock_mime.urls.return_value = [mock_url]

    # 模拟 manager.add_item_filter 返回添加成功的项
    added_item = ShelfItem(name="test_file.txt", path="/path/to/test_file.txt", item_type=ItemType.FILE)
    mock_shelf_manager.add_item_filter.return_value = [added_item]
    mock_shelf_manager.count.return_value = 1

    # 执行
    controller.handle_incoming_data(mock_mime)

    # 验证
    mock_shelf_manager.add_item_filter.assert_called_once()
    mock_window.render_items.assert_called_once_with([added_item])
    mock_window.update_count.assert_called_once_with(1)


def test_handle_incoming_data_empty(controller, mock_shelf_manager):
    """测试传入空的 MIME 数据"""
    controller.handle_incoming_data(None)
    mock_shelf_manager.add_item_filter.assert_not_called()


def test_handle_item_delete(controller, mock_shelf_manager, mock_window):
    """测试删除单项逻辑"""
    item = ShelfItem(name="test.txt", path="/test.txt", item_type=ItemType.FILE)
    mock_shelf_manager.count.return_value = 0

    controller.handle_item_delete(item)

    mock_shelf_manager.remove_item.assert_called_once_with(item)
    mock_window.remove_item_widget_by_data.assert_called_once_with(item)
    mock_window.update_count.assert_called_once_with(0)


def test_handle_item_selection_changed(controller):
    """测试选中状态的维护（多选集合）"""
    item1 = ShelfItem(name="1.txt", path="/1.txt", item_type=ItemType.FILE)
    item2 = ShelfItem(name="2.txt", path="/2.txt", item_type=ItemType.FILE)

    # 选中 item1 和 item2
    controller.handle_item_selection_changed(item1, True)
    controller.handle_item_selection_changed(item2, True)
    assert item1 in controller._selected
    assert item2 in controller._selected
    assert len(controller._selected) == 2

    # 取消选中 item1
    controller.handle_item_selection_changed(item1, False)
    assert item1 not in controller._selected
    assert item2 in controller._selected
    assert len(controller._selected) == 1


def test_handle_drag_end(controller):
    """测试拖拽结束清理状态"""
    controller._drag_pos = QPoint(10, 10)
    controller.handle_drag_end()
    assert controller._drag_pos is None


@patch("app.controllers.shelf_controller.QDrag")
def test_handle_item_drag_out_single(mock_qdrag_class, controller, mock_shelf_manager, mock_window):
    """测试单项向外拖拽（非多选或单选拖拽，复制后不删除原文件 - 假设 DropAction 为 CopyAction 且触发删除逻辑取决于实现）"""
    # 注意：根据你的源码，只要 drop_action != IgnoreAction，就会执行删除原文件逻辑。
    mock_drag_instance = mock_qdrag_class.return_value
    mock_drag_instance.exec.return_value = Qt.DropAction.CopyAction

    item = ShelfItem(name="file.txt", path="/file.txt", item_type=ItemType.FILE)

    # 执行外发拖拽
    controller.handle_item_drag_out(item, QPoint(0, 0))

    # 验证是否调用了底层删除及视图移除
    mock_shelf_manager.remove_item.assert_called_once_with(item)
    mock_window.middle_component.remove_item_widget.assert_called_once_with(item)
    mock_window.footer_component.update_count.assert_called_once_with(mock_shelf_manager.count())