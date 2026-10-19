import os
import sys
import pytest

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
    unique_key = item_file.get_unique_key()
    assert unique_key != ""
    assert unique_key == os.path.normpath(os.path.abspath("./test.txt"))

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
    # 协议和主机名不区分大小写，但路径大小写与尾部斜杠必须保留。
    url1 = ShelfItem(name="Google", item_type=ItemType.URL, url="WWW.Example.com/Path/")
    assert url1.get_unique_key() == "http://www.example.com/Path/"

    upper_path = ShelfItem(name="a", item_type=ItemType.URL, url="https://example.com/File")
    lower_path = ShelfItem(name="b", item_type=ItemType.URL, url="https://example.com/file")
    trailing_slash = ShelfItem(name="c", item_type=ItemType.URL, url="https://example.com/File/")
    assert upper_path.get_unique_key() != lower_path.get_unique_key()
    assert upper_path.get_unique_key() != trailing_slash.get_unique_key()

    # 当前策略保留 query 原文，不擅自改变参数顺序。
    url_q1 = ShelfItem(name="q1", item_type=ItemType.URL, url="https://api.test.com/search?b=2&a=1")
    url_q2 = ShelfItem(name="q2", item_type=ItemType.URL, url="https://api.test.com/search?a=1&b=2")
    assert url_q1.get_unique_key() != url_q2.get_unique_key()


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
