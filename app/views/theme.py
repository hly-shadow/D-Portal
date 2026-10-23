#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
D-Portal 统一主题配置.

功能:
    1. 定义浅色与深色主题的颜色和基础视觉参数;
    2. 检测当前系统主题;
    3. 向界面组件提供统一的主题配置;

注意:
    - 所以颜色值统一在 THEMES 中维护;
    - 两套主题拥有完全一致的配置键;
    - get_theme_colors() 返回配置副本, 避免调用方修改全局配置;
"""

from copy import deepcopy
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

# ============================================================
# 主题配置
# ============================================================
THEMES: dict[str, dict[str, Any]] = {
    # --------------------------------------------------------
    # 浅色主题
    # --------------------------------------------------------
     "light": {
        # 窗口
        "window_bg": "#E9EDF4",
        "window_border": "#D3DCE8",

        # 通用面板：顶部、底部
        "panel_bg": "#FFFFFF",
        "panel_border": "#D3DCE8",

        # 中间内容区域
        "middle_bg": "#F4F6FA",
        "middle_border": "#DFE5ED",

        # 文件卡片
        "card_bg": "#FFFFFF",
        "card_hover_bg": "#F7FAFF",
        "card_border": "#D8E1ED",

        # 文件预览区域
        "preview_bg": "#F6F8FB",

        # 滚动条
        "scrollbar": "#C7D0DD",
        "scrollbar_hover": "#AAB7C8",

         # 普通文字
         "text_color": "#1D2939",
         "sub_text_color": "#65748B",
         "disabled_text": "#98A2B3",

        # 选中状态
        "selected_bg": "#EDF4FF",
        "selected_border": "#83ACF5",
        "selected_text": "#245DA8",

         # 拖放状态
         "drop_bg": "#EAF3FF",
         "drop_border": "#4388E8",

         # 危险操作：关闭按钮等
         "danger_bg": "#FDECEC",
         "danger_hover_bg": "#FADADA",
         "danger_text": "#C93737",

         # 禁用状态
         "disabled_bg": "#F2F4F7",
         "disabled_border": "#E4E7EC",

        # 字体
        "font_family": (
            '"Segoe UI", "Microsoft YaHei UI", sans-serif'
        ),

        # 圆角
        "radius": "12px",
        "card_radius": "10px",
    },
    # --------------------------------------------------------
    # 深色主题
    # --------------------------------------------------------
    "dark": {
        # 窗口
        "window_bg": "#202020",
        "window_border": "#3A3A3A",

        # 通用面板：顶部、底部
        "panel_bg": "#2B2B2B",
        "panel_border": "#3A3A3A",

        # 中间内容区域
        "middle_bg": "transparent",
        "middle_border": "#3A3A3A",

        # 文件卡片
        "card_bg": "#2B2B2B",
        "card_hover_bg": "#353535",
        "card_border": "#3A3A3A",

        # 文件预览
        "preview_bg": "#252525",

        # 滚动条
        "scrollbar": "#555555",
        "scrollbar_hover": "#707070",

        # 普通文字
        "text_color": "#FFFFFF",
        "sub_text_color": "#AAAAAA",
        "disabled_text": "#777777",

        # 选中状态
        "selected_bg": "rgba(0, 120, 212, 30%)",
        "selected_border": "#3B99FC",
        "selected_text": "#6CB6FF",

        # 拖放状态
        "drop_bg": "#26384A",
        "drop_border": "#3B99FC",

        # 危险操作：关闭按钮等
        "danger_bg": "#513238",
        "danger_hover_bg": "#653B42",
        "danger_text": "#FFB4B4",

        # 禁用状态
        "disabled_bg": "#303030",
        "disabled_border": "#414141",

        # 字体
        "font_family": (
            '"Microsoft YaHei UI", "Segoe UI", sans-serif'
        ),

        # 圆角
        "radius": "8px",
        "card_radius": "8px",
    },
}

# ============================================================
# 主题配置校验
# ============================================================
def validate_themes() -> None:
    """检查所有主题是否拥有完全一致的配置键。"""
    if "light" not in THEMES or "dark" not in THEMES:
        raise ValueError("THEMES 必须同时包含 light 和 dark 主题")

    light_keys = set(THEMES["light"])
    dark_keys = set(THEMES["dark"])

    if light_keys != dark_keys:
        missing_in_dark = sorted(light_keys - dark_keys)
        missing_in_light = sorted(dark_keys - light_keys)

        raise ValueError(
            "浅色与深色主题的配置键不一致："
            f"dark 缺少 {missing_in_dark}；"
            f"light 缺少 {missing_in_light}"
        )

# ============================================================
# 主题获取接口
# ============================================================
def get_current_color_scheme() -> str:
    """返回当前系统主题: light 或 dark.

    当 Qt 无法明确检测到深色模式时, 默认使用浅色主题.
    """
    app = QGuiApplication.instance()
    if app is None:
        return "light"
    try:
        scheme = QGuiApplication.styleHints().colorScheme()
    except (AttributeError, RuntimeError):
        return "light"

    if scheme == Qt.ColorScheme.Dark:
        return "dark"

    return "light"

def get_theme_colors(scheme: str | None = None) -> dict[str, Any]:
    """
    获取主题配置副本.
    :param scheme:
        "light": 浅色主题
        "dark":  深色主题
        None:    自动跟随当前系统主题
    :return: 当前主题的字典副本
    """
    if scheme is None:
        scheme = get_current_color_scheme()
    if scheme not in THEMES:
        raise ValueError(
            f"不支持的主题：{scheme!r}，"
            "可选值为 'light' 或 'dark'"
        )
    return deepcopy(THEMES[scheme])

# 导入模块时立即检查配置完整性.
validate_themes()
