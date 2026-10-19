import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from app.views.components.common_widget import DraggableCardWidget, ElidedLabel


@pytest.fixture(scope="session")
def qapp():
    """确保整个测试会话期间只有一个 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestDraggableCardWidget:
    """针对 DraggableCardWidget 组件的测试类"""

    def test_default_initialization(self, qapp):
        """测试默认参数初始化（水平方向）"""
        card = DraggableCardWidget()

        # 验证基础属性与布局类型
        assert card is not None
        assert card._drag_pos is None
        # 验证默认是水平布局
        assert card.layout() is not None

    def test_vertical_initialization(self, qapp):
        """测试垂直方向初始化"""
        card = DraggableCardWidget(orientation=Qt.Orientation.Vertical)

        assert card is not None
        assert card.layout() is not None

    def test_custom_margins_and_spacing(self, qapp):
        """测试自定义边距和间距"""
        custom_margins = (10, 20, 10, 20)
        custom_spacing = 15
        card = DraggableCardWidget(
            margins=custom_margins,
            spacing=custom_spacing
        )

        layout = card.layout()
        assert layout.spacing() == custom_spacing
        # 验证 margins 是否符合预期
        margins = layout.contentsMargins()
        assert (margins.left(), margins.top(), margins.right(), margins.bottom()) == custom_margins


class TestElidedLabel:
    """针对 ElidedLabel 组件的测试类"""

    def test_label_initialization(self, qapp):
        """测试文本标签初始化"""
        label = ElidedLabel("测试文本")

        assert label._full_text == "测试文本"
        assert label.minimumWidth() == 20

    def test_set_text(self, qapp):
        """测试动态设置文本内容"""
        label = ElidedLabel()
        label.setText("新的长文本测试")

        assert label._full_text == "新的长文本测试"


