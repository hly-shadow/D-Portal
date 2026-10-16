from typing import override
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QMouseEvent, QFontMetrics
from PySide6.QtWidgets import QLabel
from qfluentwidgets import CardWidget, IconWidget

class DraggableCardWidget(CardWidget):
    """支持拖拽宿主窗口移动的CardWidget"""
    def __init__(self,icon: IconWidget, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self.icon_widget = icon
        self.icon_widget.setFixedSize(24,24)

    @override
    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.window().animation.state() == QPropertyAnimation.State.Running:
                self.window().animation.stop() # 如果正在播放动画, 先停止动画
            self._drag_pos = e.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            e.accept()
        else:
            super().mousePressEvent(e)

    @override
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            # 移动主窗口
            self.window().move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    @override
    def mouseReleaseEvent(self, e: QMouseEvent):
        self._drag_pos = None
        self.window().leaveEvent(e)
        super().mouseReleaseEvent(e)

class ElidedLabel(QLabel):
    """显示单行文本, 超过宽度时用省略号代替"""
    def __init__(self, text='', parent=None):
        super().__init__(parent)
        self._full_text = text
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setToolTip(text)
        self.setMinimumWidth(20)
        self.setText(text)

    def set_full_text(self, text: str):
        self._full_text = text
        self.setToolTip(text)
        self._update_elided_text()

    def _update_elided_text(self):
        metrics = QFontMetrics(self.font())
        width = self.width()
        if width > 0:
            elided = metrics.elidedText(
                self._full_text,
                Qt.TextElideMode.ElideMiddle,
                width
            )
            if self.text() != elided:
                self.setText(elided)
        # self.setText(
        #     metrics.elidedText(
        #         self._full_text,
        #         Qt.TextElideMode.ElideMiddle,
        #         max(0, self.contentsRect().width())
        #     )
        # )

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided_text()