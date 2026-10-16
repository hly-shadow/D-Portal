import pytest
from unittest.mock import MagicMock

from app.models.shelf_manager import ShelfManager
from app.models.data_model import ShelfItem, ItemType
from app.controllers.shelf_controller import ShelfController
from app.views.shelf_window import ShelfWindow


@pytest.fixture
def mock_window():
    """使用 MagicMock 虚拟一个 ShelfWindow，避免单元测试时弹窗"""
    return MagicMock(spec=ShelfWindow)


@pytest.fixture
def shelf_manager():
    """提供一个真实的 ShelfManager 实例（Model层）"""
    return ShelfManager()


@pytest.fixture
def controller(shelf_manager, mock_window):
    """初始化控制器实例"""
    return ShelfController(shelf_manager, mock_window)


def test_controller_initialization(shelf_manager, mock_window):
    """测试控制器初始化时是否会自动刷新一次视图"""
    controller = ShelfController(shelf_manager, mock_window)

    # 验证初始化时，视图的 render_items 收到的空数据应该是个字典 {}
    mock_window.render_items.assert_called_once_with({}, set())
    assert controller._selected_keys == set()


def test_handle_item_delete(controller, shelf_manager, mock_window):
    """测试控制器处理删除项的逻辑"""
    item = ShelfItem(name="test.txt", item_type=ItemType.FILE, path="/test.txt")
    shelf_manager.add_item(item)
    assert shelf_manager.count() == 1

    # 触发删除
    controller.handle_item_delete(item)

    # 验证 manager 中是否成功移除了该项
    assert shelf_manager.count() == 0


def test_handle_item_selected_toggle(controller, mock_window):
    """测试右键点击选中与取消选中的状态切换逻辑"""
    item = ShelfItem(name="doc.pdf", item_type=ItemType.FILE, path="/doc.pdf")
    key = item.get_unique_key()

    # 1. 第一次点击：选中
    controller.handle_item_selected(item)

    assert key in controller._selected_keys
    # 验证是否指挥 window 更新了对应 key 的选中状态（传 True）
    mock_window.update_selected_state.assert_called_with(key, True)

    # 2. 第二次点击：取消选中
    controller.handle_item_selected(item)

    assert key not in controller._selected_keys
    # 验证是否指挥 window 更新了对应 key 的选中状态（传 False）
    mock_window.update_selected_state.assert_called_with(key, False)


def test_refresh_view(controller, shelf_manager, mock_window):
    """测试手动刷新视图是否能正确将数据传递给 View"""
    item = ShelfItem(name="image.png", item_type=ItemType.FILE, path="/image.png")
    shelf_manager.add_item(item)

    controller._selected_keys.add(item.get_unique_key())

    # 调用刷新
    controller.refresh_view()

    # 验证 window.render_items 收到了字典和选中 keys 集合
    mock_window.render_items.assert_called_with(
        shelf_manager.items,  # 这里是字典
        controller._selected_keys
    )