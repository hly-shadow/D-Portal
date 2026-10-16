import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication
from qfluentwidgets import TransparentToolButton

from app.models.data_model import ShelfItem, ItemType
from app.views.components.item_widget import ShelfItemWidget


@pytest.fixture
def sample_item():
    """提供一个标准的测试数据项"""
    return ShelfItem(
        name="测试文件.txt",
        item_type=ItemType.FILE,
        path="/path/to/test.txt"
    )


def test_widget_initialization(qtbot, sample_item):
    """测试组件初始化状态与尺寸"""
    widget = ShelfItemWidget(sample_item)
    qtbot.addWidget(widget)

    # 验证基本属性
    assert widget.item == sample_item
    assert widget.is_selected is False
    assert widget.height() == 65


def test_update_selected_style(qtbot, sample_item):
    """测试选中状态切换及样式改变"""
    widget = ShelfItemWidget(sample_item)
    qtbot.addWidget(widget)

    # 1. 切换为选中状态
    widget.update_selected(True)
    assert widget.is_selected is True
    assert "border: 2px solid #0078d4" in widget.styleSheet()

    # 2. 切换回未选中状态
    widget.update_selected(False)
    assert widget.is_selected is False
    assert widget.styleSheet() == ""


def test_delete_signal_emission(qtbot, sample_item):
    """测试点击删除按钮是否能正确发射 delete_signal"""
    widget = ShelfItemWidget(sample_item)
    qtbot.addWidget(widget)

    # 使用 qtbot 监视 delete_signal 信号的发射
    with qtbot.waitSignal(widget.delete_signal, timeout=1000) as blocker:
        # 在组件中查找删除按钮 (TransparentToolButton)
        delete_btns = widget.findChildren(TransparentToolButton)
        assert len(delete_btns) > 0

        # 模拟点击删除按钮
        qtbot.mouseClick(delete_btns[0], Qt.MouseButton.LeftButton)

    # 验证信号是否成功触发，且传出的参数是正确的 item
    assert blocker.signal_triggered
    assert blocker.args[0] == sample_item


def test_right_click_selection_signal(qtbot, sample_item):
    """测试右键点击时是否能正确发射 selection_signal"""
    widget = ShelfItemWidget(sample_item)
    qtbot.addWidget(widget)

    # 监视 selection_signal
    with qtbot.waitSignal(widget.selection_signal, timeout=1000) as blocker:
        # 模拟在组件上进行右键点击
        qtbot.mouseClick(widget, Qt.MouseButton.RightButton)

    # 验证是否成功发出选中信号
    assert blocker.signal_triggered
    assert blocker.args[0] == sample_item