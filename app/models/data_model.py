#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, os
import hashlib
import urllib.parse
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

class ItemType(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    URL = "url"
    TEXT = "text"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class ShelfItem:
    name: str # 显示名称
    item_type: ItemType # 类型
    # 根据类型存放具体内容
    path: Optional[str] = None # 仅用于 FILE/DIRECTORY 的本地路径
    url: Optional[str] = None # 仅用于 URL 的网页链接
    content: Optional[str] = None # 仅用于 TEXT 的文本内容
    # 内部缓存文本的 MD5,避免重复计算
    _text_hash: Optional[str] = field(init=False, repr=False, compare=False, default=None)

    def __post_init__(self):
        # 初始化时预计算文本哈希（如果有内容）
        if self.item_type == ItemType.TEXT and self.content:
            object.__setattr__(self, '_text_hash', hashlib.md5(self.content.encode("utf-8")).hexdigest())

    def get_unique_key(self) -> str:
        """根据不同的类型返回对应的唯一标识，用于去重"""
        if self.item_type in (ItemType.FILE, ItemType.DIRECTORY):
            if not self.path:
                return ""
            # 转换为绝对路径，解决相对路径（如 "./abc" 和 "abc"）不一致问题
            abs_path = os.path.abspath(self.path)
            # 规范化路径（统一斜杠方向、去除多余的斜杠等）
            normalized_path = os.path.normpath(abs_path)
            # 根据操作系统决定是否转小写
            # Windows (win32) 不区分大小写，转小写以防重复
            if sys.platform.startswith("win"):
                return normalized_path.lower()
            # Linux 严格区分大小写，保持原样
            else:
                return normalized_path

        elif self.item_type == ItemType.URL:
            if not self.url:
                return ""
            url = self.url.strip()
            parsed = urllib.parse.urlparse(url)

            scheme = parsed.scheme.lower() # 如果没写协议，就是空字符串 ""
            netloc = parsed.netloc.lower()
            # 主机名/协议不区分大小写；路径保留原大小写和末尾斜杠
            path = parsed.path

            query_str = f"?{parsed.query}" if parsed.query else ""
            fragment_str = f"#{parsed.fragment}" if parsed.fragment else ""

            if scheme:
                return f"{scheme}://{netloc}{path}{query_str}{fragment_str}"
            return f"//{netloc}{path}{query_str}{fragment_str}"

        elif self.item_type == ItemType.TEXT:
            return self._text_hash if self._text_hash else ""

        return ""