#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PySide6.QtCore import QObject, QEvent, Qt

from app.views.components.top_widget import TopComponent


class MainWindowEventFilter(QObject):
    def __init__(self, window, controller):
        super().__init__(window)
        self.window = window
        self.controller = controller
        # 建立事件类型与处理函数的映射表
        # 这里事件类型很少, 所以直接使用(反射字典)的方式
        self.event_map = {
            QEvent.Type.MouseButtonPress: self._on_mouse_press,
            QEvent.Type.MouseMove: self._on_mouse_move,
            QEvent.Type.MouseButtonRelease: self._on_mouse_release,
            QEvent.Type.DragEnter: self._on_drag_enter,
            QEvent.Type.Drop: self._on_drop
        }
    # 【核心】事件过滤器, 根据事件类型反射调用相应的方法
    def eventFilter(self,obj, event):
        handler = self.event_map.get(event.type())
        if handler:
            handler(event)
            return True
        return super().eventFilter(obj, event)


    def _on_drag_enter(self, event):
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()

    def _on_drop(self, event):
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
        self.controller.handle_item_add(event)

    def _on_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 通知控制器: 开始拖拽, 并传入当前鼠标的全局坐标
            self.controller.handle_drag_start(event.globalPosition().toPoint())
            event.accept()

    def _on_mouse_move(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            # 检查当前鼠标下的组件是否是空白滚动区或顶栏，而不是文件卡片
            widget = self.window.childAt(event.position().toPoint())
            # 如果当前点中的不是标题栏, 则不触发窗口拖动
            if not self._is_child_of(widget, TopComponent):
                return

            # 通知控制器: 正在拖拽, 并传入最新的全局坐标
            self.controller.handle_drag_move(event)
            event.accept()

    def _on_mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 通知控制器：拖拽结束
            self.controller.handle_drag_end()
            event.accept()

    @staticmethod
    def _is_child_of(widget, target_class):
        """辅助函数: 检查某个组件是否属于指定类型的子组件"""
        while widget:
            if isinstance(widget, target_class):
                return True
            widget = widget.parent()
        return False