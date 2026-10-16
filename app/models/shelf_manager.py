from typing import List, Dict, overload, Union

from app.models.data_model import ShelfItem

class ShelfManager:
    def __init__(self):
        self._items: Dict[str, ShelfItem] = {}

    @property
    def items(self) -> Dict[str, ShelfItem]:
        return self._items.copy()

    def add_item_filter(self, items: List[ShelfItem]) -> List[ShelfItem]:
        """
        过滤掉重复的数据, 并把合法的真·新数据加入到管理器中
        返回需要 VIEW 层渲染的数据
        """
        truly_new_items = []
        for item in items:
            unique_key = item.get_unique_key()
            if not unique_key:
                raise ValueError("Item unique key cannot be empty or None.")
            if unique_key not in self._items:
                truly_new_items.append(item)
                self._items[unique_key] = item
            else:
                print(f"检测到重复数据，已过滤: {unique_key}")
        return truly_new_items

    @overload
    def remove_item(self, target: ShelfItem) -> bool:
        ...
    @overload
    def remove_item(self, target: str) -> bool:
        ...

    def remove_item(self, target: Union[ShelfItem, str]) -> bool:
        if isinstance(target, ShelfItem):
            key = target.get_unique_key()
        elif isinstance(target, str):
            key = target
        else:
            raise TypeError("remove_item 仅支持传入 ShelfItem 实例或 str 类型的 key")
        if key in self._items:
            del self._items[key]
            return True
        return False

    def clear(self) -> None:
        self._items.clear()

    def count(self) -> int:
        return len(self._items)