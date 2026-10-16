import sys

from PySide6.QtWidgets import QApplication

from app.views.shelf_window import ShelfWindow

def run():
    app = QApplication(sys.argv)
    app.setApplicationName("D-Portal")
    window = ShelfWindow()

    window.show()
    sys.exit(app.exec())
