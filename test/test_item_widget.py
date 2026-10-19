import sys
import pytest
from unittest.mock import patch
from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QSignalSpy


# 确保存在全局的 QApplication 实例
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


# 模拟主题颜色等外部依赖，避免在无完整应用上下文时报错
@pytest.fixture(autouse=True)
def mock_app_dependencies():
    with patch("app.views.theme.get_theme_colors") as mock_theme:
        mock_theme.return_value = {
            "selected_bg": "#000000",
            "selected_border": "#111111",
            "card_hover_bg": "#222222",
            "card_bg": "#333333",
            "card_border": "#444444",
            "text_color": "#ffffff",
            "font_family": "Arial"
        }
        yield


from app.views.components.item_widget import ShelfItemWidget


class DummyShelfItem:
    def __init__(self, name="Test File", path=None):
        self.name = name
        self.path = path


@pytest.fixture
def shelf_item():
    return DummyShelfItem(name="Sample Document.txt", path=None)


@pytest.fixture
def widget(qapp, shelf_item):
    w = ShelfItemWidget(shelf_item)
    w.show()
    return w


def test_widget_initialization(widget, shelf_item):
    """测试组件初始化是否正确加载了数据和默认状态"""
    assert widget.item == shelf_item
    assert widget.name_label.text() == shelf_item.name
    assert not widget.is_selected
    assert not widget.is_hovered


def test_set_selected(widget):
    """测试选中状态切换及 selection_signal 信号的触发"""
    spy = QSignalSpy(widget.selection_signal)

    widget.set_selected(True)
    assert widget.is_selected is True

    # 将 len(spy) 修改为 spy.count()
    assert spy.count() == 1
    assert spy.at(0) == [widget.item, True]


def test_hover_events(widget):
    """测试鼠标悬浮（进入和离开）事件是否正确更新悬浮状态"""
    # 模拟鼠标进入，传入合法的 QEvent
    enter_event = QEvent(QEvent.Type.Enter)
    widget.enterEvent(enter_event)
    assert widget.is_hovered is True

    # 模拟鼠标离开，传入合法的 QEvent
    leave_event = QEvent(QEvent.Type.Leave)
    widget.leaveEvent(leave_event)
    assert widget.is_hovered is False


def test_right_click_selection(widget):
    """测试右键点击是否能够切换选中状态"""
    assert not widget.is_selected

    # 使用 QTest 模拟在 widget 中心进行鼠标右键点击
    QTest.mouseClick(widget, Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier)

    # 验证是否成功切换为选中状态
    assert widget.is_selected is True

    # 再次右键点击，验证是否能取消选中
    QTest.mouseClick(widget, Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier)
    assert widget.is_selected is False


def test_delete_button_signal(widget):
    """测试删除信号是否能被正常监听并触发"""
    spy = QSignalSpy(widget.delete_signal)

    # 手动触发删除信号
    widget.delete_signal.emit(widget.item)

    # 将 len(spy) 修改为 spy.count()
    assert spy.count() == 1
    assert spy.at(0)[0] == widget.item