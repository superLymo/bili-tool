import sys, asyncio, pathlib
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QStyle,
    QPushButton,
    QFileDialog,
)
from PySide6.QtGui import QPixmap, QPalette, QIcon
from PySide6.QtCore import Qt, QByteArray
from bilibili_api import emoji, Credential
import aiofiles, aiohttp, qasync
from utils.config_loader import userConf
from core import emoji_handler as emo


class emoListItem(QWidget):
    def __init__(self, pixmap, name, id, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.emoPkgName: str = name
        self.emoPkgId: int = id

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(36, 36)
        self.icon_label.setScaledContents(True)
        self.icon_label.setPixmap(pixmap)

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignVCenter)

        layout.addWidget(self.icon_label)
        layout.addStretch()
        layout.addWidget(self.name_label)
        layout.addStretch()


class emoSearchListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("ImageSearchListWidget")
        self.setWindowTitle("表情包搜索 - 双击即可下载")
        self.setWindowIcon(QIcon(str(userConf.getDefaultIco())))

        self._emoPkgs = {}
        self._emoListItems = []
        self._saveFolder: str = ""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        search_layout = QHBoxLayout()

        self.search_edit = QLineEdit(placeholderText="输入表情包名搜索...")

        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.on_search_clicked)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_button)

        self.list_widget = QListWidget()
        self.list_widget.doubleClicked.connect(self.on_item_double_click)
        self.list_widget.setUniformItemSizes(True)

        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.list_widget)

        self.update_styles()
        self.resize(400, 400)

        app: QApplication = QApplication.instance()
        app.paletteChanged.connect(self.update_styles)

    def add_item(self, pix, name, id):
        item = QListWidgetItem(self.list_widget)
        widget = emoListItem(pix, name, id)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.setItemWidget(item, widget)
        self._emoListItems.append((item, widget))

    @qasync.asyncSlot()
    async def searchEmoByName(self):
        if not self._emoPkgs:
            self._emoPkgs = await emo.getAllEmojiPackages()

        pkgs = await emo.searchMatchEmoji(self._emoPkgs, self.search_edit.text())

        self.setWindowTitle(f"搜索完毕 - {len(pkgs)}个结果")

        if not pkgs:
            self.search_button.setEnabled(True)

            return

        async with aiohttp.ClientSession() as session:
            for pkg in pkgs:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
                    "Referer": pkg["url"],
                }

                async with session.get(pkg["url"], headers=headers) as response:
                    coverImage = await response.read()

                    coverImgPix = QPixmap()
                    coverImgPix.loadFromData(QByteArray(coverImage))

                    self.add_item(coverImgPix, pkg["text"], int(pkg["id"]))

        self.search_button.setEnabled(True)

    def on_search_clicked(self):
        self.list_widget.clear()
        self._emoListItems.clear()
        self.search_button.setEnabled(False)

        self.searchEmoByName()

    @qasync.asyncSlot()
    async def on_item_double_click(self, index):
        emoItem = self.list_widget.itemWidget(self.list_widget.item(index.row()))

        if not emoItem:
            return

        selectedFolder = QFileDialog.getExistingDirectory(
            self, "选择表情包下载目录", self._saveFolder
        )

        if not selectedFolder:
            return

        self._saveFolder = selectedFolder

        await emo.downloadPkg(
            emoItem.emoPkgId, pathlib.Path(self._saveFolder) / emoItem.emoPkgName
        )

        self.setWindowTitle(f"下载完毕 - {emoItem.emoPkgName}")

    def is_dark_theme(self):
        app: QApplication = QApplication.instance()

        bg_color = app.palette().color(QPalette.Window)
        brightness = (
            bg_color.red() * 299 + bg_color.green() * 587 + bg_color.blue() * 114
        ) / 1000
        return brightness < 128

    def update_styles(self):
        dark = self.is_dark_theme()

        # 基础颜色配置
        colors = {
            "bg": "#2D2D30" if dark else "#F5F5F5",
            "widget_bg": "#1E1E1E" if dark else "#FFFFFF",
            "border": "#3E3E42" if dark else "#E0E0E0",
            "text": "#E1E1E1" if dark else "#212121",
            "placeholder": "#858585" if dark else "#757575",
            "hover": "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.04)",
            "selected": "rgba(0,151,251,0.3)" if dark else "rgba(66,133,244,0.2)",
            "focus": "#0097FB" if dark else "#4285F4",
            "scroll_bg": "#424242" if dark else "#F5F5F5",
            "scroll_handle": "#686868" if dark else "#BDBDBD",
        }

        # 按钮渐变颜色
        if dark:
            colors.update(
                {
                    "gradient_start": "#0097FB",
                    "gradient_end": "#007ACC",
                    "gradient_hover_start": "#1AA7FF",
                    "gradient_hover_end": "#0097FB",
                    "gradient_pressed_start": "#007ACC",
                    "gradient_pressed_end": "#005A9E",
                }
            )
            rgb_focus = "0,151,251"
        else:
            colors.update(
                {
                    "gradient_start": "#4285F4",
                    "gradient_end": "#3367D6",
                    "gradient_hover_start": "#5C9BF5",
                    "gradient_hover_end": "#4285F4",
                    "gradient_pressed_start": "#3367D6",
                    "gradient_pressed_end": "#2A56C4",
                }
            )
            rgb_focus = "66,133,244"

        qss = f"""
            /* 主背景 */
            QWidget#ImageSearchListWidget {{ background-color: {colors["bg"]}; }}
            
            /* 搜索框样式 */
            QLineEdit {{
                background: {colors["widget_bg"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                selection-background-color: {colors["selected"]};
            }}
            QLineEdit:focus {{ border: 2px solid {colors["focus"]}; padding: 7px 11px; }}
            QLineEdit::placeholder {{ color: {colors["placeholder"]}; font-style: italic; }}
            
            /* 搜索按钮样式 - 现代渐变版 */
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors["gradient_start"]}, 
                    stop:1 {colors["gradient_end"]});
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 20px;
                font-size: 14px;
                font-weight: 500;
                margin-left: 8px;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors["gradient_hover_start"]}, 
                    stop:1 {colors["gradient_hover_end"]});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors["gradient_pressed_start"]}, 
                    stop:1 {colors["gradient_pressed_end"]});
            }}
            QPushButton:disabled {{
                background: {colors["border"]};
                color: {colors["placeholder"]};
                opacity: 0.6;
            }}
            
            /* 列表控件样式 */
            QListWidget {{
                background: {colors["widget_bg"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                padding: 4px;
                outline: none;
                font-size: 13px;
            }}
            QListWidget::item {{
                background: transparent;
                border-radius: 6px;
                padding: 2px;
                margin: 2px 0;
            }}
            QListWidget::item:hover {{ background: {colors["hover"]}; }}
            QListWidget::item:selected {{ background: {colors["selected"]}; }}
            
            /* 滚动条样式 */
            QScrollBar:vertical {{ background: {colors["scroll_bg"]}; width: 12px; border-radius: 6px; }}
            QScrollBar::handle:vertical {{ background: {colors["scroll_handle"]}; border-radius: 6px; min-height: 30px; }}
            QScrollBar::handle:vertical:hover {{ background: {colors["focus"]}; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
            
            /* 列表项子控件 */
            ImageItemWidget, QLabel {{ background: transparent; border: none; }}
        """

        self.setStyleSheet(qss)
