import sys
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QPoint
from utils import config_loader


class biliTrayRegister:
    def __init__(
        self,
        trayIconParent: QApplication,
        trayMenuParent: QWidget,
        onShowCallback,
        onExitCallback,
    ):
        trayIconParent.setQuitOnLastWindowClosed(False)

        self._trayIcon = None
        self._trayMenu = None

        self._onShowActionCLicked = onShowCallback
        self._onExitActionClicked = onExitCallback

        self._createTrayIcon(trayIconParent)
        self._createTrayMenu(trayMenuParent)

        if sys.platform != "win32":
            self._trayIcon.setContextMenu(self._trayMenu)

        self._trayIcon.activated.connect(self._onTrayActivated)
        self._trayIcon.show()

    def _showTrayMenu(self):
        trayGeo = self._trayIcon.geometry()
        menuSize = self._trayMenu.sizeHint()

        coverX = -16
        coverY = 16

        menuX = trayGeo.right() + coverX
        menuY = trayGeo.top() - menuSize.height() + coverY

        self._trayMenu.exec(QPoint(menuX, menuY))

    def _onTrayActivated(self, reason):
        if sys.platform == "win32":
            if reason == QSystemTrayIcon.Trigger:
                self._onShowActionCLicked()
            elif reason == QSystemTrayIcon.Context:
                self._showTrayMenu()
        else:
            if reason == QSystemTrayIcon.Trigger:
                self._onShowActionCLicked()

    def _createTrayIcon(self, parent: QApplication):
        self._trayIcon = QSystemTrayIcon(parent)

        self._trayIcon.setIcon(QIcon(str(config_loader.userConf.getDefaultIco())))
        self._trayIcon.setToolTip("透明GIF/图片显示工具（性能优化版）")

    def _createTrayMenu(self, parent: QWidget):
        self._trayMenu = QMenu(parent)
        self._trayMenu.setObjectName("TrayMenu")

        self._trayMenu.setStyleSheet(
            """
        QMenu#TrayMenu {
            padding: 4px 2px;  /* 菜单上下内边距缩小 */
            border-radius: 12px;  /* 轻量圆角，不增加过多渲染开销 */
        }
        QMenu#TrayMenu::item {
            padding: 8px 16px 8px 32px;  /* 菜单项内边距缩小 */
            margin: 0 2px;      /* 菜单项外边距缩小 */
            border-radius: 6px; /* 新增：菜单项圆角（值可根据需求调整） */
        }
        QMenu#TrayMenu::item:selected {
            background-color: palette(highlight);  /* 系统原生高亮背景 */
            color: palette(highlightedText);       /* 系统原生高亮文字色 */
            border-radius: 6px; /* 新增：选中态也保留圆角，视觉统一 */
        }
        """
        )

        showAction = QAction("显示界面", self._trayMenu)
        showAction.triggered.connect(self._onShowActionCLicked)

        exitAction = QAction("退出应用", self._trayMenu)
        exitAction.triggered.connect(self._onExitActionClicked)

        self._trayMenu.addAction(showAction)
        self._trayMenu.addSeparator()
        self._trayMenu.addAction(exitAction)
