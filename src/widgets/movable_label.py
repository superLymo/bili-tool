import random
from PySide6.QtWidgets import (
    QLabel
)
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPainter, QPen


class movableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self._init_style()

    def _init_style(self):
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: white;
                font-weight: bold;
                /* 添加内边距，确保文字完整显示 */
                padding-left: 2px;
                padding-right: 2px;
                padding-top: 1px;
                padding-bottom: 1px;
            }
        """)

        self.adjustSize()

    def activeMotion(self, startPos : QPoint, endPos : QPoint):
        self.move(startPos)

        animation = QPropertyAnimation(self, b"pos", self)

        # 设置动画的起始和结束值
        animation.setStartValue(startPos)
        animation.setEndValue(endPos)

        animation.setDuration(random.randint(12000, 20000))
        animation.setEasingCurve(QEasingCurve.Type.Linear)

        animation.finished.connect(self._onMotionFinished)
        
        self.show()
        animation.start()

    def _onMotionFinished(self):
        self.deleteLater()

    def paintEvent(self, event):
        painter = QPainter(self)

        # 开启抗锯齿，使边缘更平滑
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # 获取绘制区域
        rect = self.rect()

        # 调整绘制区域，确保文字完整显示
        # 向内缩进1像素，避免文字被截断
        draw_rect = rect.adjusted(1, 1, -1, -1)

        # 获取文本
        text = self.text()

        # 设置字体
        painter.setFont(self.font())

        # 创建画笔用于描边
        # 使用细黑色描边，解决描边过重问题
        outline_color = QColor(0, 0, 0, 180)  # 黑色，半透明
        outline_pen = QPen(outline_color)
        outline_pen.setWidth(2)  # 描边宽度减少到2像素，解决描边过重问题

        # 创建画笔用于主文字
        text_color = QColor(255, 255, 255)  # 白色文字
        text_pen = QPen(text_color)
        text_pen.setWidth(1)

        # 优化描边效果：使用4个方向的细描边
        # 相比8个方向的描边，4个方向更轻量，不会过于沉重
        painter.setPen(outline_pen)

        # 4个方向的偏移（上、下、左、右）
        offsets = [
            (-1, 0),  # 左
            (1, 0),  # 右
            (0, -1),  # 上
            (0, 1),  # 下
        ]

        for dx, dy in offsets:
            # 在每个偏移位置绘制描边文字
            painter.drawText(
                draw_rect.translated(dx, dy), Qt.AlignmentFlag.AlignCenter, text
            )

        # 绘制主文字
        painter.setPen(text_pen)
        painter.drawText(draw_rect, Qt.AlignmentFlag.AlignCenter, text)