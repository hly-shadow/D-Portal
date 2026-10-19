from unittest.mock import MagicMock, patch
import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication

from app.models.data_model import ShelfItem, ItemType
from app.models.shelf_manager import ShelfManager
from app.controllers.shelf_controller import ShelfController


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


class FakeSignal:
    def connect(self, callback):
        pass


@pytest.fixture
def view():
    result = MagicMock()
    for name in (
        "item_delete_requested", "item_selection_requested", "item_drag_requested",
        "close_requested", "window_drag_started", "window_drag_moved",
        "window_drag_ended", "external_drop_requested",
    ):
        setattr(result, name, FakeSignal())
    result.dock_manager = MagicMock()
    return result


@pytest.fixture
def setup_controller(qapp, view):
    manager = ShelfManager()
    controller = ShelfController(manager, view)
    return controller, manager, view


def test_selection_uses_stable_keys(setup_controller):
    controller, _manager, _view = setup_controller
    first = ShelfItem("a", ItemType.FILE, path="/tmp/a")
    controller.handle_item_selection_changed(first, True)
    assert first.get_unique_key() in controller._selected_keys
    controller.handle_item_selection_changed(first, False)
    assert first.get_unique_key() not in controller._selected_keys


def test_delete_updates_model_and_view(setup_controller):
    controller, manager, view = setup_controller
    item = ShelfItem("a", ItemType.FILE, path="/tmp/a")
    manager.add_item_filter([item])
    controller.handle_item_delete(item)
    assert manager.count() == 0
    view.remove_item.assert_called_once_with(item)
    view.set_item_count.assert_called_once_with(0)


def test_incoming_data_adds_existing_local_file(setup_controller, tmp_path):
    controller, manager, view = setup_controller
    path = tmp_path / "example.txt"
    path.write_text("test", encoding="utf-8")
    mime = MagicMock()
    mime.hasUrls.return_value = True
    url = MagicMock()
    url.isLocalFile.return_value = True
    url.toLocalFile.return_value = str(path)
    mime.urls.return_value = [url]

    controller.handle_incoming_data(mime)
    assert manager.count() == 1
    view.add_items.assert_called_once()
    view.set_item_count.assert_called_once_with(1)


def test_drag_out_only_removes_on_copy_action(setup_controller):
    controller, manager, view = setup_controller
    item = ShelfItem("a", ItemType.FILE, path="/tmp/a")
    manager.add_item_filter([item])
    with patch("app.controllers.shelf_controller.QDrag") as drag_class:
        drag_class.return_value.exec.return_value = Qt.DropAction.IgnoreAction
        controller.handle_item_drag_out(item, QPoint())
    assert manager.count() == 1
    view.remove_item.assert_not_called()


def test_drag_out_copy_removes_only_dragged_item(setup_controller):
    controller, manager, view = setup_controller
    first = ShelfItem("a", ItemType.FILE, path="/tmp/a")
    second = ShelfItem("b", ItemType.FILE, path="/tmp/b")
    manager.add_item_filter([first, second])
    with patch("app.controllers.shelf_controller.QDrag") as drag_class:
        drag_class.return_value.exec.return_value = Qt.DropAction.CopyAction
        controller.handle_item_drag_out(first, QPoint())
    assert manager.count() == 1
    assert manager.get_item(second.get_unique_key()) == second
    view.remove_item.assert_called_once_with(first)
