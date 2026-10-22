#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt

THEMES = {
     "light": {
        # 主窗口：浅蓝灰色
        "window_bg": "#E9EDF4",
        "panel_border": "#D3DCE8",

        # 标题栏与底部状态栏：纯白
        "panel_bg": "#FFFFFF",

        # 中间内容区域：极浅蓝灰色
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

        # 选中状态
        "selected_bg": "#EDF4FF",
        "selected_border": "#83ACF5",
        "selected_text": "#245DA8",

        # 文字
        "text_color": "#1D2939",
        "sub_text_color": "#65748B",

        "font_family": (
            '"Segoe UI", "Microsoft YaHei UI", sans-serif'
        ),

        "radius": "12px",
        "card_radius": "10px",
    },

    "dark": {
        # 1. 窗口与面板基础色
        "window_bg": "#202020",  # 主窗口深灰底色
        "panel_bg": "#2B2B2B",  # 顶栏/底栏深色面板背景
        "panel_border": "#3A3A3A",  # 面板边框

        # 2. 中间滚动区域与容器
        "middle_bg": "transparent",  # 中间滚动区通透
        "middle_border": "#3A3A3A",  # 容器边框

        # 3. 卡片常规状态
        "card_bg": "#2B2B2B",  # 卡片默认深灰背景
        "card_hover_bg": "#353535",  # 卡片鼠标悬浮深色背景
        "card_border": "#3A3A3A",  # 卡片边框

        # 4. 卡片选中状态
        "selected_bg": "rgba(0, 120, 212, 30%)",  # 选中背景（深色下沉浸式蓝微透）
        "selected_border": "#3B99FC",  # 选中边框
        "selected_text": "#6CB6FF",  # 选中文字高亮色

        # 5. 字体与常规文本
        "text_color": "#FFFFFF",  # 主文本色（纯白）
        "sub_text_color": "#AAAAAA",  # 次级文本
        "font_family": '"Microsoft YaHei", "Segoe UI", sans-serif',
        "radius": "8px",
    }
}


def get_current_color_scheme() -> str:
    """自动判断当前系统是深色还是浅色模式"""
    is_dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    return "dark" if is_dark else "light"


def get_theme_colors() -> dict:
    """获取当前系统匹配的完整主题颜色字典"""
    scheme = get_current_color_scheme()
    return THEMES[scheme]