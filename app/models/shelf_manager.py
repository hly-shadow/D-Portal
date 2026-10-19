#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""纯业务数据管理, 不依赖 Qt 界面。"""

from collections.abc import Iterable

from app.models.data_model import ShelfItem

class ShelfManager:
    def __init__(self):
        self._items: dict[str, ShelfItem] = {}

    @property
    def items(self) -> dict[str, ShelfItem]:
        """返回副本, 避免外部直接修改数据."""
        return self._items.copy()

    def add_item_filter(self, items: Iterable[ShelfItem]) -> list[ShelfItem]:
        """
        过滤重复项目: 无效 key 的项目跳过, 不让单个坏数据中断整批操作.
        """
        added: list[ShelfItem] = []
        for item in items:
            if not isinstance(item, ShelfItem):
                continue
            key = item.get_unique_key()
            if not key or key in self._items:
                continue
            self._items[key] = item
            added.append(item)
        return added

    def remove_item(self, target: ShelfItem | str) -> bool:
        if isinstance(target, ShelfItem):
            key = target.get_unique_key()
        elif isinstance(target, str):
            key = target
        else:
            raise TypeError("remove_item 仅支持传入 ShelfItem 实例或唯一键字符串")
        return self._items.pop(key, None) is not None

    def get_item(self, key: str) -> ShelfItem | None:
        return self._items.get(key)

    def get_items_by_keys(self, keys: Iterable[str]) -> list[ShelfItem]:
        """按当前列表顺序返回指定 key 的项目."""
        wanted = set(keys)
        return [item for key, item in self._items.items() if key in wanted]

    def clear(self) -> None:
        self._items.clear()

    def count(self) -> int:
        return len(self._items)
