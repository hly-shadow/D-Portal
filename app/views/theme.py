#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt

THEMES = {
    "light": {
        # 1. 窗口与面板基础色
        "window_bg": "#F3F3F3",  # 主窗口底色
        "panel_bg": "#FFFFFF",  # 顶栏/底栏背景色
        "panel_border": "#E1E1E1",  # 面板边框

        # 2. 中间滚动区域与容器
        "middle_bg": "transparent",  # 中间滚动区保持通透，与底座融合
        "middle_border": "#E1E1E1",  # 容器边框

        # 3. 卡片常规状态
        "card_bg": "#FFFFFF",  # 卡片默认背景
        "card_hover_bg": "#F8F9FA",  # 卡片鼠标悬浮背景
        "card_border": "#E1E1E1",  # 卡片边框

        # 4. 卡片选中状态
        "selected_bg": "rgba(0, 120, 212, 10%)",  # 选中背景（浅蓝色微透）
        "selected_border": "#0078D4",  # 选中边框
        "selected_text": "#004085",  # 选中文字高亮色

        # 5. 字体与常规文本
        "text_color": "#212529",  # 主文本色
        "sub_text_color": "#6C757D",  # 次级文本/统计栏文字
        "font_family": '"Microsoft YaHei", "Segoe UI", sans-serif',
        "radius": "8px",  # 统一个圆角
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