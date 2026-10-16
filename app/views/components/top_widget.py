from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout

from qfluentwidgets import (
    SubtitleLabel,
    CaptionLabel,
    FluentIcon,
    TransparentToolButton,
    IconWidget
)

from app.views.components.common_widget import DraggableCardWidget
from app.config import ICON_PATH

class TopComponent(DraggableCardWidget):
    close_requested = Signal()

    def __init__(self, title: str = "D-Portal", subtitle: str = "Shelf", parent=None):
        super().__init__(orientation=Qt.Orientation.Horizontal, margins=(16, 12, 8, 12), spacing=8, parent=parent)
        self.title = title
        self.subtitle = subtitle

        self._init_ui()

    def _init_ui(self):

        # 左侧图标
        icon_widget = IconWidget(ICON_PATH)
        icon_widget.setFixedSize(24, 24)

        # 中间文字区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        title = SubtitleLabel(self.title, self)
        subtitle = CaptionLabel(self.subtitle, self)

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)


        # 右侧关闭按钮
        close_btn = TransparentToolButton(self)
        close_btn.setIcon(FluentIcon.CLOSE)
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.close_requested.emit)

        # 5. 组装到布局中
        self.layout_box.addWidget(icon_widget)
        self.layout_box.addLayout(text_layout)
        self.layout_box.addStretch(1)
        self.layout_box.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignTop)