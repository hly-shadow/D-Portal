import sys

from PySide6.QtWidgets import QApplication

from app.core.shelf_manager import ShelfManager
from app.ui.shelf_window import ShelfWindow

def run():
    app = QApplication(sys.argv)
    shelf_manager = ShelfManager()

    app.setApplicationName("D-Portal")
    window = ShelfWindow(shelf_manager)

    window.show()
    sys.exit(app.exec())