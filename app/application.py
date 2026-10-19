#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""应用组合根: 创建 Model/View/Controller 并连接依赖."""
import sys
from PySide6.QtWidgets import QApplication

from app.models.shelf_manager import ShelfManager
from app.views.shelf_window import ShelfWindow
from app.controllers.shelf_controller import ShelfController


def create_application(argv=None):
    app = QApplication(sys.argv if argv is None else argv)
    app.setApplicationName("D-Portal")

    model = ShelfManager()
    view = ShelfWindow()
    controller = ShelfController(model, view)

    # 返回并由 run() 持有引用, 避免对象被垃圾回收.
    return app, view, controller


def run():
    app, window, _controller = create_application()
    window.show()
    sys.exit(app.exec())