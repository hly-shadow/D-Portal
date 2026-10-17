# D-Portal 项目设计
## 背景

在日常使用中，你是否经常遇到这样的场景：
- 需要将不同目录下的素材图片拖入 **Photoshop** 中；
- 或者需要把分散在各处的文件拷贝、归集到同一个文件夹。

如果每次都要在多个资源管理器窗口之间来回切换，过程会非常繁琐。

本项目正是为了解决这一痛点而生，让文件的暂存与调用变得轻量而高效。

## 项目介绍
- 🛠️ **项目简介**：基于 Python + PySide 6 开发的 Windows 本地文件暂存工具。
- ⚙️ **技术栈**：Python、PySide 6、MVC 架构。
- 💡 **核心功能**：支持将文件暂存至工具中，方便在其他窗口间高效使用。
- 📌 **当前状态**：持续完善中，欢迎交流与指正！
## 基本使用

<img src="https://picgocloud.com/m/af22bb7d-c1c5-42ad-bc1c-25fe1fa1e389.gif" width="800" alt="操作演示">
<img src="https://picgocloud.com/m/6b7ed38e-7dfe-4eeb-9702-30bc0e4048b9.gif" width="800" alt="操作演示">
<img src="https://picgocloud.com/m/725ef0ef-796f-4bf1-9cd1-cd7ad4fed58b.gif" width="800" alt="操作演示">

**上述操作只是复制, 并不会修改原文件.**
## D-Portal 含义
- D: 表示Drag-and-Drop，表示Windows下核心的交互方式;
- Portal:传送门，文件通过它到达任意一个地方;
## ICON

![ICON](https://picgocloud.com/m/7147ec7c-97b7-40fa-a87d-42e19eb17d80.png)

## 项目结构
```text
D-Portal/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── application.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── shelf_manager.py
│   │   └── data_model.py
│   │
│   ├── view/
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── bottom_widget.py
│   │   │   ├── common_widget.py
│   │   │   ├── item_widget.py
│   │   │   ├── middle_widget.py
│   │   │   ├── top_widget.py
│   │   │   └──
│   │   ├── __init__.py 
│   │   ├── shelf_window.py
│   │   └── theme.py
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── shelf_controller.py
│   │
│   ├── components
│   │   ├── __init__.py
│   │   ├── edge_dock_manager.py
│   │   └── event_filter.py
│   └── config.py
│
├── resources/
│   ├── icons/
│   │   └── favicon.ico
│   
├── tests/
│
├── requirements.txt
├── README.md
└── .gitignore
```
## 未来计划和问题说明
问题说明:
- 界面样式比较简陋, 特别是系统在深色模式下;
- 没有设置界面, 不能个性化设置;
- 未进行多屏幕的测试;
- 编程水平有限, 代码写的并不优雅,会有未知问题;

计划:
- 美化界面;
- 增加设置窗口
- 优化交互逻辑;
- ...