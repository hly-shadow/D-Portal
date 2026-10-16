from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QApplication, QVBoxLayout

from qframelesswindow import AcrylicWindow

from app.components.event_filter import MainWindowEventFilter
from app.components.edge_dock_manager import EdgeAutoDockManager, DockEdge
from app.views.components.item_widget import ShelfItemWidget
from app.views.components.bottom_widget import FooterComponent
from app.views.components.middle_widget import MiddleComponent
from app.views.components.top_widget import TopComponent


from app.models.shelf_manager import ShelfManager

from app.config import APP_NAME, SHELF_WIDTH, SHELF_HEIGHT

class ShelfWindow(AcrylicWindow):
    item_delete_requested = Signal(object)
    select_requested = Signal(object)
    drag_requested = Signal(object, QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shelf_manager = ShelfManager()
        self.top_component = TopComponent(parent=self)
        self.middle_component = MiddleComponent(parent=self)
        self.footer_component = FooterComponent(parent=self)

        # 【关键】在这里进行局部导入，避开顶部循环依赖
        from app.controllers.shelf_controller import ShelfController
        self.controller = ShelfController(self.shelf_manager, self)

        self.middle_component.delete_signal.connect(self.controller.handle_item_delete)
        self.middle_component.selection_changed_signal.connect(
            self.controller.handle_item_selection_changed
        )
        self.middle_component.item_drag_signal.connect(
            self.controller.handle_item_drag_out
        )
        # 初始化管理器
        self.dock_manager = EdgeAutoDockManager(self, trigger_margin=15, hide_margin=5)
        self.event_filter = MainWindowEventFilter(self, self.controller)
        self.installEventFilter(self.event_filter)
        self._init_window()
        self._init_ui()

    def _init_window(self):
        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.titleBar.hide()

        screen = QApplication.primaryScreen().availableGeometry()
        self.dock_manager.set_dock_edge(DockEdge.RIGHT)
        initial_x = screen.right()
        initial_y = screen.top() + (screen.height() - SHELF_HEIGHT) // 2
        self.setGeometry(initial_x, initial_y, SHELF_WIDTH, SHELF_HEIGHT)
        self.setAcceptDrops(True)  # 允许接收外部拖入

    def _init_ui(self):
        """主窗口布局组装：加载顶、中、底各个组件"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(4)
        # ==================== 1.加载顶部组件 ====================
        main_layout.addWidget(self.top_component)

        # ==================== 2.加载中间滚动区域组件==============
        main_layout.addWidget(self.middle_component, 1)

        # ==================== 3.加载底部卡片组件=================
        main_layout.addWidget(self.footer_component)

    def render_items(self, items: list):
        self.middle_component.add_item_widget(items)

    def remove_item_widget_by_data(self, item):
        """
        根据数据对象, 在 MiddleComponent 组件中找到对应的卡片并销毁它
        """
        self.middle_component.remove_item_widget(item)

    def update_count(self, count: int):
        self.footer_component.update_count(count)