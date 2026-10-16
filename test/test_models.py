import pytest
from app.models.data_model import ShelfItem, ItemType

def test_shelf_item_url_normalization():
    """测试 URL 去重和规范化逻辑是否正确"""
    item1 = ShelfItem(name="百度1", item_type=ItemType.URL, url="www.baidu.com")
    item2 = ShelfItem(name="百度2", item_type=ItemType.URL, url="http://www.baidu.com")
    item3 = ShelfItem(name="百度3", item_type=ItemType.URL, url="Www.baidu.com/")

    # 它们的唯一 Key 应该完全一致
    assert item1.get_unique_key() == item2.get_unique_key()
    assert item2.get_unique_key() == item3.get_unique_key()
