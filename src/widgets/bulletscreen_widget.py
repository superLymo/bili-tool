import random, platform
from ctypes import windll, c_int, WINFUNCTYPE
import win32con, win32gui
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QPoint
from widgets import movable_label
from core import blivedm_signal


class bullscrContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._containerHeight = 0

        self._initWindow()

        blivedm_signal.bldmEmitter.messageLoaded.connect(self.addDanmu)

    def setClickThrough(self):
        hwnd = int(self.winId())
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        ex_style |= win32con.WS_EX_TRANSPARENT   
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

    def _initWindow(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        self._containerHeight = screen_height // 3

        self.setGeometry(0, 0, screen_width, self._containerHeight)

    def addDanmu(self, prefix, text):
        damnuLabel = movable_label.movableLabel(text, parent=self)

        min_y = 20
        max_y = self._containerHeight - damnuLabel.height() - 5  # 下边距5像素
        fin_y = 0

        # 确保区间有效
        if min_y < max_y:
            fin_y = random.randint(min_y, max_y)
        else:
            fin_y = 20

        damnuLabel.activeMotion(
            QPoint(self.width(), fin_y), QPoint(-damnuLabel.width(), fin_y)
        )

    def showEvent(self, event):
        super().showEvent(event)

        if platform.system() == 'Windows':
            self.setClickThrough()