import os
import sys
import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from PySide6.QtGui import QIcon


class ItemType(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    URL = "url"
    TEXT = "text"


@dataclass
class ShelfItem:
    name: str # 显示名称
    item_type: ItemType # 类型
    # 根据类型存放具体内容
    path: Optional[str] = None # 仅用于 FILE/DIRECTORY 的本地路径
    url: Optional[str] = None # 仅用于 URL 的网页链接
    content: Optional[str] = None # 仅用于 TEXT 的文本内容

    icon: Optional[QIcon] = None

    def get_unique_key(self) -> str:
        """根据不同的类型返回对应的唯一标识，用于去重"""
        if self.item_type in (ItemType.FILE, ItemType.DIRECTORY):
            if not self.path:
                return ''
            # 规范化路径（统一斜杠方向、去除多余的斜杠等）
            normalized_path = os.path.normpath(self.path)

            # 根据操作系统决定是否转小写
            # Windows (win32) 不区分大小写，转小写以防重复
            if sys.platform.startswith('win'):
                return normalized_path.lower()
            # Linux 严格区分大小写，保持原样
            else:
                return normalized_path
        elif self.item_type == ItemType.URL:
            return self.url.strip() if self.url else ""
        elif self.item_type == ItemType.TEXT:
            if not self.content:
                return ""
            return hashlib.md5(self.content.encode('utf-8')).hexdigest()

        return ''
