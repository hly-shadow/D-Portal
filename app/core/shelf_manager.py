from typing import List

from .shelf_item import ShelfItem

class ShelfManager:

    def __init__(self):
        self._items: List[ShelfItem] = []
        self._existing_keys: set[str] = set()

    @property
    def items(self) -> List[ShelfItem]:
        return self._items.copy()

    def add_item(self, item: ShelfItem) -> None:
        key = item.get_unique_key()
        if not key:
            return
        if key in self._existing_keys:
            return

        self._items.append(item)
        self._existing_keys.add(key)

    def remove_item(self, item: ShelfItem) -> None:
        if item in self._items:
            key = item.get_unique_key()
            if key in self._existing_keys:
                self._existing_keys.remove(key)

            self._items.remove(item)

    def clear(self) -> None:
        self._items.clear()
        self._existing_keys.clear()

    def count(self) -> int:
        return len(self._items)

