# D-Portal 项目设计
## 一.名称含义
- D: 表示Drag-and-Drop，表示Windows下核心的交互方式;
- Portal:传送门，文件通过它到达任意一个地方;
## 二.ICON

## 三.项目结构
```text
D-Portal/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── shelf_manager.py
│   │   ├── shelf_item.py
│   │   └── application.py
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── shelf_window.py
│   │   ├── shelf_item_widget.py
│   │   └── widgets.py
│   │
│   └── config.py
│
├── resources/
│   ├── icons/
│
├── tests/
│
├── requirements.txt
├── README.md
└── .gitignore
```