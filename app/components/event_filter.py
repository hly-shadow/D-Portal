#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""把窗口级 Qt 事件转换为 View 信号, 不直接依赖 Controller."""
from PySide6.QtCore import QObject, QEvent, Qt, Signal, QPoint

from app.views.components.top_widget import TopComponent


class MainWindowEventFilter(QObject):
    window_drag_started = Signal(QPoint)
    window_drag_moved = Signal(object)
    window_drag_ended = Signal()
    external_drop_requested = Signal(object)

    def __init__(self, window):
        super().__init__(window)
        self.window = window
        # 建立事件类型与处理函数的映射表
        # 这里事件类型很少, 所以直接使用(反射字典)的方式
        self.event_map = {
            QEvent.Type.MouseButtonPress: self._on_mouse_press,
            QEvent.Type.MouseMove: self._on_mouse_move,
            QEvent.Type.MouseButtonRelease: self._on_mouse_release,
            QEvent.Type.DragEnter: self._on_drag_enter,
            QEvent.Type.DragMove: self._on_drag_move,
            QEvent.Type.Drop: self._on_drop
        }
    # 【核心】事件过滤器, 根据事件类型反射调用相应的方法
    def eventFilter(self,obj, event):
        handler = self.event_map.get(event.type())
        if handler is None:
            return super().eventFilter(obj, event)
        handler(event)
        # 仅拦截拖放事件: 鼠标事件继续交给 Qt 控件正常处理.
        if event.type() in (QEvent.Type.DragEnter, QEvent.Type.DragMove, QEvent.Type.Drop):
            return event.isAccepted()
        return False


    def _on_drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def _on_drag_move(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def _on_drop(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
        self.external_drop_requested.emit(event.mimeData())

    def _on_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.window_drag_started.emit(event.globalPosition().toPoint())

    def _on_mouse_move(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        widget = self.window.childAt(event.position().toPoint())
        if self._is_child_of(widget, TopComponent):
            self.window_drag_moved.emit(event)

    def _on_mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.window_drag_ended.emit()

    @staticmethod
    def _is_child_of(widget, target_class):
        """辅助函数: 检查某个组件是否属于指定类型的子组件"""
        while widget:
            if isinstance(widget, target_class):
                return True
            widget = widget.parent()
        return False