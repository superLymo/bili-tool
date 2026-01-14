import datetime, asyncio
from typing import Optional
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)
from PySide6.QtCore import Qt, QSize, QByteArray, Signal
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor
import qasync, aiohttp

from core import video_handler


class videoCard(QFrame):
    videoLoaded = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_style()

        self._vdo: Optional[video_handler.bapi.video.Video] = None
        self._currentBvid: str = ""

    def setup_ui(self):
        # 主垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 1. 标题（居中）
        self.lbl_title = QLabel("")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setWordWrap(True)
        main_layout.addWidget(self.lbl_title)

        # 2. 封面图片（居中）
        self.lbl_cover = QLabel()
        self.lbl_cover.setFixedSize(320, 180)
        self.lbl_cover.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_cover)

        # 3. 底部信息（左右）
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(4)

        self.lbl_author = QLabel("        ")
        self.lbl_author.setStyleSheet("color: #888;")
        bottom_layout.addWidget(self.lbl_author)

        self.lbl_time = QLabel("          ")
        self.lbl_time.setStyleSheet("color: #555; font-size: 11px;")
        bottom_layout.addWidget(self.lbl_time, 1, Qt.AlignRight)

        main_layout.addLayout(bottom_layout)

    def setup_style(self):
        # self.setStyleSheet("""
        #     border: 1px solid #ddd;
        #     border-radius: 6px;
        # """)

        pass

    def getCurrentBvid(self) -> str:
        return self._currentBvid

    @qasync.asyncSlot()
    async def setVideo(self, vdoBv: str):
        self._vdo = video_handler.getVideo(vdoBv)
        self._currentBvid = vdoBv

        vdoInfo = await self._vdo.get_info()

        self.lbl_title.setText(vdoInfo["title"])
        self.lbl_author.setText(vdoInfo["owner"]["name"])
        self.lbl_time.setText(
            datetime.datetime.fromtimestamp(vdoInfo["pubdate"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
                "Referer": vdoInfo["pic"],
            }

            async with session.get(vdoInfo["pic"], headers=headers) as response:
                coverImage = await response.read()

                coverImgPix = QPixmap()
                coverImgPix.loadFromData(QByteArray(coverImage))

                if not coverImgPix.isNull():
                    coverImgPix = coverImgPix.scaled(
                        320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )

                    self.lbl_cover.setPixmap(coverImgPix)

        self.videoLoaded.emit()
