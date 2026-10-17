import sys
import pytest
from PySide6.QtGui import QIcon

from app.models.data_model import ShelfItem, ItemType  # 请根据实际项目路径调整导入


def test_shelf_item_file_directory_key():
    """测试文件和目录类型的唯一键生成（绝对路径、规范化及平台大小写敏感性）"""
    # 1. 测试普通文件路径
    item_file = ShelfItem(
        name="test.txt",
        item_type=ItemType.FILE,
        path="./test.txt"
    )
    # 唯一键应该被转为绝对且规范化的路径
    assert item_file.get_unique_key() != ""
    assert not item_file.get_unique_key().endswith("test.txt") or os_is_normalized(item_file.get_unique_key())

    # 2. 测试 Windows 平台下路径转小写特性
    item_path1 = ShelfItem(name="a.txt", item_type=ItemType.FILE, path="/Folder/Sub/File.txt")
    item_path2 = ShelfItem(name="a.txt", item_type=ItemType.FILE, path="/Folder/sub/file.txt")

    key1 = item_path1.get_unique_key()
    key2 = item_path2.get_unique_key()

    if sys.platform.startswith("win"):
        assert key1 == key2  # Windows 下不区分大小写
    else:
        assert key1 != key2  # Linux/macOS 下区分大小写


def test_shelf_item_empty_path():
    """测试文件/目录路径为空时的处理"""
    item = ShelfItem(name="empty", item_type=ItemType.FILE, path="")
    assert item.get_unique_key() == ""


def test_shelf_item_url_normalization():
    """测试 URL 类型的规范化与唯一键生成（协议、域名、路径尾部斜杠、Query 参数排序）"""
    # 1. 测试自动补全 http 协议、路径去尾部斜杠、域名/路径小写
    url1 = ShelfItem(name="Google", item_type=ItemType.URL, url="WWW.Example.com/Path/")
    url2 = ShelfItem(name="Google2", item_type=ItemType.URL, url="http://www.example.com/path")
    assert url1.get_unique_key() == url2.get_unique_key()
    assert url1.get_unique_key() == "http://www.example.com/path"

    # 2. 测试 Query 参数排序与保留
    url_q1 = ShelfItem(name="q1", item_type=ItemType.URL, url="https://api.test.com/search?b=2&a=1")
    url_q2 = ShelfItem(name="q2", item_type=ItemType.URL, url="https://api.test.com/search?a=1&b=2")
    # 参数顺序不同，但规范化后 Query 会被排序，因此唯一键应相同
    assert url_q1.get_unique_key() == url_q2.get_unique_key()
    assert url_q1.get_unique_key() == "https://api.test.com/search?a=1&b=2"


def test_shelf_item_empty_url():
    """测试 URL 为空时的处理"""
    item = ShelfItem(name="empty", item_type=ItemType.URL, url="")
    assert item.get_unique_key() == ""


def test_shelf_item_text_hash():
    """测试文本类型的 MD5 哈希预计算与唯一键获取"""
    content = "Hello, Shelf World!"
    item = ShelfItem(name="note", item_type=ItemType.TEXT, content=content)

    # 验证是否成功预计算了 _text_hash 并且 get_unique_key 返回该哈希
    assert item._text_hash is not None
    assert len(item._text_hash) == 32  # MD5 长度为 32 位
    assert item.get_unique_key() == item._text_hash


def test_shelf_item_empty_text():
    """测试文本内容为空时的处理"""
    item = ShelfItem(name="empty", item_type=ItemType.TEXT, content="")
    assert item._text_hash is None
    assert item.get_unique_key() == ""


def test_shelf_item_unknown_type():
    """测试未知类型的唯一键生成"""
    item = ShelfItem(name="unknown", item_type=ItemType.UNKNOWN)
    assert item.get_unique_key() == ""


def test_shelf_item_frozen_and_immutability():
    """测试 dataclass(frozen=True) 是否生效（不可变对象）"""
    item = ShelfItem(name="test", item_type=ItemType.TEXT, content="abc")
    with pytest.raises(Exception):  # 尝试修改冻结对象的属性应抛出异常
        item.name = "new_name"


def test_shelf_item_icon_compare_exclusion():
    """测试 icon 字段不参与对象比较（compare=False）"""
    icon1 = QIcon()
    icon2 = QIcon()

    item1 = ShelfItem(name="file", item_type=ItemType.FILE, path="/test.txt", icon=icon1)
    item2 = ShelfItem(name="file", item_type=ItemType.FILE, path="/test.txt", icon=icon2)

    # 尽管 icon 对象不同，但因为配置了 compare=False，两者应当相等
    assert item1 == item2


def os_is_normalized(path: str) -> bool:
    """辅助判断路径是否为绝对路径"""
    import os
    return os.path.isabs(path)