import pathlib
from typing import Optional
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QFileDialog,
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor, QIcon
import qasync

from core import video_handler
from widgets import video_card_widget
from utils import config_loader


class vdoDownWidget(QWidget):
    readyToDestory = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_style()

        self._currentVdo: Optional[video_handler.bapi.video.Video] = None
        self._currentDownFolder: str = ""

    def setup_ui(self):
        self.setWindowTitle("视频助手")
        self.setWindowIcon(QIcon(str(config_loader.userConf.getDefaultIco())))

        # 主垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignTop)

        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("请输入视频的BV号...")
        self.edit_search.setFixedHeight(32)
        search_layout.addWidget(self.edit_search, 1)

        self.btn_search = QPushButton("搜索")
        self.btn_search.setFixedSize(60, 32)
        self.btn_search.clicked.connect(self.onSearchButtonClicked)
        search_layout.addWidget(self.btn_search)

        self.down_search = QPushButton("下载")
        self.down_search.setFixedSize(60, 32)
        self.down_search.setEnabled(False)
        self.down_search.clicked.connect(self.onDownButtonClicked)
        search_layout.addWidget(self.down_search)

        main_layout.addLayout(search_layout)

        # 卡片区域
        self.card = video_card_widget.videoCard()
        self.card.videoLoaded.connect(self.onCardVideoLoaded)
        main_layout.addWidget(self.card, alignment=Qt.AlignHCenter)

        self.adjustSize()

    def setup_style(self):
        self.edit_search.setStyleSheet("""
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 0 10px;
        """)

        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: #fff;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
            QPushButton:pressed {
                background-color: #2A56C6;
            }
            QPushButton:disabled {
                background-color: #E8EAED;
                color: #000;                                                    
            }
        """)

        self.down_search.setStyleSheet("""
            QPushButton {
                background-color: #0FA958;
                color: #fff;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0D954D;
            }
            QPushButton:pressed {
                background-color: #0B8142;
            }
            QPushButton:disabled {
                background-color: #E6F4EA;
                color: #000;                                                     
            }
        """)

    def setBtnsEnabled(self, ena: bool):
        self.btn_search.setEnabled(ena)
        self.down_search.setEnabled(ena)

    def onCardVideoLoaded(self):
        self.setBtnsEnabled(True)

    def onSearchButtonClicked(self):
        inputBv = self.edit_search.text()

        if inputBv == "":
            return

        self.setBtnsEnabled(False)

        self.card.setVideo(inputBv)

    @qasync.asyncSlot()
    async def onDownButtonClicked(self):
        self.setBtnsEnabled(False)

        selectedFolder = QFileDialog.getExistingDirectory(
            self, "选择视频下载目录", self._currentDownFolder
        )

        if selectedFolder == "":
            self.setBtnsEnabled(True)

            return

        self._currentDownFolder = selectedFolder

        await video_handler.downloadVideosV2(
            self.card._vdo,
            pathlib.Path(self._currentDownFolder) / self.card.getCurrentBvid(),
        )

        self.setBtnsEnabled(True)
        self.setWindowTitle(f"{self.card.getCurrentBvid()} - 下载完成")

    def closeEvent(self, event):
        self.readyToDestory.emit()