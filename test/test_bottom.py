import pytest
from qfluentwidgets import BodyLabel

from app.views.components.bottom_widget import FooterComponent


def test_footer_initialization(qtbot):
    """测试底部组件的初始状态与默认显示文案"""
    footer = FooterComponent()
    qtbot.addWidget(footer)

    # 验证是否成功创建了 BodyLabel 组件
    count_label = footer.findChild(BodyLabel)
    assert count_label is not None

    # 验证初始数量为 0 时，文案是否正确渲染为 "0 items"
    assert count_label.text() == "0 items"


@pytest.mark.parametrize(
    "input_count, expected_text",
    [
        (0, "0 items"),
        (1, "1 item"),    # 单数形式校验
        (2, "2 items"),   # 复数形式校验
        (15, "15 items"), # 大数字复数校验
    ],
)
def test_update_count(qtbot, input_count, expected_text):
    """使用参数化测试验证不同数量下的单复数文案渲染"""
    footer = FooterComponent()
    qtbot.addWidget(footer)

    # 调用更新数量方法
    footer.update_count(input_count)

    # 获取组件内的 BodyLabel 并检查文本
    count_label = footer.findChild(BodyLabel)
    assert count_label.text() == expected_text
