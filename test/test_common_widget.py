import pytest
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, QPoint
from app.views.components.common_widget import DraggableCardWidget, ElidedLabel


# 1. 全局共享的 QApplication fixture（整个测试会话只初始化一次）
@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


# ==================== 测试组 1：ElidedLabel 组件测试 ====================

def test_elided_label(app):
    """测试省略号标签的基础功能"""
    label = ElidedLabel("测试长文本自动省略效果")
    assert label.text() is not None

    # 模拟调整尺寸
    label.resize(200, 30)
    assert label.width() == 200

    # 压窄尺寸验证不会崩溃
    label.resize(30, 30)
    app.processEvents()


# ==================== 测试组 2：DraggableCardWidget 组件测试 ====================

def test_draggable_card_widget(app):
    """测试可拖拽卡片容器的初始化与布局方向"""
    # 测试默认水平布局
    card_h = DraggableCardWidget(orientation=Qt.Orientation.Horizontal)
    assert card_h.layout_box is not None

    # 测试垂直布局
    card_v = DraggableCardWidget(orientation=Qt.Orientation.Vertical)
    assert card_v.layout_box is not None


def test_draggable_card_drag_move(qtbot):
    """测试拖拽卡片容器是否能成功带动宿主窗口移动"""

    # 1. 创建主窗口并显示
    window = QMainWindow()
    window.resize(400, 300)
    window.move(100, 100)  # 设置初始坐标为 (100, 100)

    # 2. 创建可拖拽卡片并放入窗口
    card = DraggableCardWidget(parent=window)
    window.setCentralWidget(card)
    window.show()

    # 确保窗口已经正确加载到屏幕上
    qtbot.addWidget(window)

    # 记录移动前的窗口坐标
    initial_window_pos = window.pos()
    assert initial_window_pos == QPoint(100, 100)

    # 3. 获取卡片正中心的位置（相对卡片本身）
    card_center = card.rect().center()

    # 4. 模拟鼠标交互过程：
    # (1) 在卡片中心按下鼠标左键
    qtbot.mousePress(card, Qt.MouseButton.LeftButton, pos=card_center)

    # (2) 模拟鼠标向右下方移动 50 像素（触发拖拽）
    # qtbot.mouseMove 接受目标 widget 和移动后的局部坐标
    target_pos = card_center + QPoint(50, 50)
    qtbot.mouseMove(card, pos=target_pos)

    # 5. 断言：验证主窗口的坐标是否随着鼠标的拖拽而发生了改变
    new_window_pos = window.pos()
    assert new_window_pos != initial_window_pos, "拖拽鼠标后，窗口坐标应当发生变化！"

    # 6. 模拟释放鼠标左键
    qtbot.mouseRelease(card, Qt.MouseButton.LeftButton, pos=target_pos)