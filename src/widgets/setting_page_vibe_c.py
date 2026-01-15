from PySide6.QtWidgets import (
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFileDialog,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
import pathlib
import aiohttp
import qasync
from utils import config_loader, sovits_http_helper


class settingPage(QWidget):
    changeCurrentImage = Signal(str)
    readyToDestory = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowIcon(QIcon(str(config_loader.userConf.getDefaultIco())))
        self.setWindowTitle("配置页面")

        self._init_ui()

        self._lastImageSelectDir : str = ""
        self._lastFfmpegSelectDir : str = ""

    def _init_ui(self):
        # ---------- 统一调宽 ----------
        self.resize(900, 720)

        # ---------- Fusion 友好样式 ----------
        # 取高亮色做主题，保证跟随系统深浅
        hl = self.palette().highlight().color()
        hl_hover = hl.lighter(110)  # hover 再亮一点
        hl_pressed = hl.darker(110)  # 按下暗一点
        text_color = self.palette().text().color().name()
        window_color = self.palette().window().color().name()
        base_color = self.palette().base().color().name()
        mid_color = self.palette().mid().color().name()

        self.setStyleSheet(f"""
            QWidget {{
                background: {window_color};
                color: {text_color};
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                font-size: 14px;
            }}
            QGroupBox {{
                border: 1px solid {mid_color};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: 600;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
            QLineEdit {{
                background: {base_color};
                border: 1px solid {mid_color};
                border-radius: 4px;
                padding: 6px 8px;
                selection-background-color: {hl};
            }}
            QLineEdit:focus {{
                border-color: {hl};
            }}
            QPushButton {{
                background: {hl};
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 7px 16px;
                font-weight: 600;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background: {hl_hover};
            }}
            QPushButton:pressed {{
                background: {hl_pressed};
            }}
            QLabel {{
                background: transparent;
            }}
            QComboBox {{
                background: {base_color};
                border: 1px solid {mid_color};
                border-radius: 4px;
                padding: 6px 8px;
                min-height: 30px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
            QComboBox:on {{
                border-color: {hl};
            }}
        """)

        # ---------- 以下布局代码完全沿用你原来的 ----------
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(16)
        mainLayout.setContentsMargins(24, 24, 24, 24)

        # ---- assetsBlock ----
        assetsBlock = QGroupBox("看板娘——可以是图片或者GIF~有默认的~", self)
        assetsBlockLayout = QVBoxLayout(assetsBlock)
        self._userAssetPath = QLineEdit(
            config_loader.userConf.getImage(),
            placeholderText="待选择...",
            parent=assetsBlock,
        )
        self._userAssetPath.setEnabled(False)
        userAssetBtn = QPushButton("选择看板娘", assetsBlock)
        userAssetBtn.clicked.connect(self.onSelectImage)
        userAssetLayout = QHBoxLayout()
        userAssetLayout.addWidget(self._userAssetPath)
        userAssetLayout.addWidget(userAssetBtn)
        assetsBlockLayout.addLayout(userAssetLayout)

        # ---- depsBlock ----
        depsBlock = QGroupBox("ffmpeg可执行文件路径——若需下载视频则填~", self)
        depsBlockLayout = QVBoxLayout(depsBlock)
        self._ffmpegPath = QLineEdit(
            config_loader.userConf.getFfmpeg(),
            placeholderText="待选择...",
            parent=depsBlock,
        )
        self._ffmpegPath.setEnabled(False)
        ffmpegBtn = QPushButton("选择Ffmpeg", depsBlock)
        ffmpegBtn.clicked.connect(self.onSelectFfmpeg)
        ffmpegLayout = QHBoxLayout()
        ffmpegLayout.addWidget(self._ffmpegPath)
        ffmpegLayout.addWidget(ffmpegBtn)
        depsBlockLayout.addLayout(ffmpegLayout)

        # ---- biliBlock ----
        biliBlock = QGroupBox("b站cookie配置——请去浏览器中获得~必填~", self)
        biliBlockLayout = QVBoxLayout(biliBlock)
        sessDataInfo = QLabel("SESSDATA: ", biliBlock)
        self._sessDataEdit = QLineEdit(
            config_loader.userConf.getSessData(),
            placeholderText="从浏览器获取的SESSDATA...",
            parent=biliBlock,
        )
        sessDataLayout = QHBoxLayout()
        sessDataLayout.addWidget(sessDataInfo)
        sessDataLayout.addWidget(self._sessDataEdit)
        biliJctInfo = QLabel("bili_jct: ", biliBlock)
        self._biliJctEdit = QLineEdit(
            config_loader.userConf.getBiliJct(),
            placeholderText="从浏览器获取的bili_jct...",
            parent=biliBlock,
        )
        biliJctLayout = QHBoxLayout()
        biliJctLayout.addWidget(biliJctInfo)
        biliJctLayout.addWidget(self._biliJctEdit)
        buvid3Info = QLabel("buvid3: ", biliBlock)
        self._buvid3Edit = QLineEdit(
            config_loader.userConf.getBuvid3(),
            placeholderText="从浏览器获取的buvid3...",
            parent=biliBlock,
        )
        buvid3Layout = QHBoxLayout()
        buvid3Layout.addWidget(buvid3Info)
        buvid3Layout.addWidget(self._buvid3Edit)
        biliBlockLayout.addLayout(sessDataLayout)
        biliBlockLayout.addLayout(biliJctLayout)
        biliBlockLayout.addLayout(buvid3Layout)

        # ---- biliveBlock ----
        biliveBlock = QGroupBox("直播间配置——若需监听直播弹幕则填~", self)
        biliveBlockLayout = QVBoxLayout(biliveBlock)
        self._liveRoomId = QLineEdit(
            str(config_loader.userConf.getLiveRoom()),
            placeholderText="8位数直播间号...",
            parent=biliveBlock,
        )
        biliveBlockLayout.addWidget(self._liveRoomId)

        # ---- biliTtsBlock ----
        biliTtsBlock = QGroupBox("GPT-SoVITS配置——若需直播弹幕语音化则填~", self)
        biliTtsBlockLayout = QVBoxLayout(biliTtsBlock)
        apiServerInfo = QLabel("api_v2地址: ", biliTtsBlock)
        self._apiServerEdit = QLineEdit(
            config_loader.userConf.getSovitsApiServer(),
            biliTtsBlock,
            placeholderText=r"示例: http://127.0.0.1/9880 ",
        )
        apiServerV2Layout = QHBoxLayout()
        apiServerV2Layout.addWidget(apiServerInfo)
        apiServerV2Layout.addWidget(self._apiServerEdit)
        gptModelInfo = QLabel("gpt模型路径: ", biliTtsBlock)
        self._gptModelEdit = QLineEdit(
            config_loader.userConf.getGptModel(),
            biliTtsBlock,
            placeholderText="运行GPT-SoVITS的服务器上的路径...",
        )
        gptModelLayout = QHBoxLayout()
        gptModelLayout.addWidget(gptModelInfo)
        gptModelLayout.addWidget(self._gptModelEdit)
        sovitsModelInfo = QLabel("sovits模型路径: ", biliTtsBlock)
        self._sovitsModelEdit = QLineEdit(
            config_loader.userConf.getSovitsModel(),
            biliTtsBlock,
            placeholderText="运行GPT-SoVITS的服务器上的路径...",
        )
        sovitsModelLayout = QHBoxLayout()
        sovitsModelLayout.addWidget(sovitsModelInfo)
        sovitsModelLayout.addWidget(self._sovitsModelEdit)
        refAudioInfo = QLabel("参考语音路径: ", biliTtsBlock)
        self._refAudioEdit = QLineEdit(
            config_loader.userConf.getRefAudio(),
            biliTtsBlock,
            placeholderText="运行GPT-SoVITS的服务器上的路径...",
        )
        refAudioLayout = QHBoxLayout()
        refAudioLayout.addWidget(refAudioInfo)
        refAudioLayout.addWidget(self._refAudioEdit)
        refTextInfo = QLabel("参考文本内容: ", biliTtsBlock)
        self._refTextEdit = QLineEdit(
            config_loader.userConf.getRefAudioText(),
            biliTtsBlock,
            placeholderText="参考语音里面的文本...",
        )
        refTextLayout = QHBoxLayout()
        refTextLayout.addWidget(refTextInfo)
        refTextLayout.addWidget(self._refTextEdit)
        refLangInfo = QLabel("参考语音/文本的语言: ", biliTtsBlock)
        self._refLangSelecter = QComboBox(parent=biliTtsBlock)
        for idx, (txt, val) in enumerate(
            [("中文", "zh"), ("英语", "en"), ("日语", "ja"), ("韩语", "ko")]
        ):
            self._refLangSelecter.addItem(txt)
            self._refLangSelecter.setItemData(idx, val)
        lang = config_loader.userConf.getRefAudioLang()
        self._refLangSelecter.setCurrentIndex(["zh", "en", "ja", "ko"].index(lang))
        refLangLayout = QHBoxLayout()
        refLangLayout.addWidget(refLangInfo)
        refLangLayout.addWidget(self._refLangSelecter)
        biliTtsBlockLayout.addLayout(apiServerV2Layout)
        biliTtsBlockLayout.addLayout(gptModelLayout)
        biliTtsBlockLayout.addLayout(sovitsModelLayout)
        biliTtsBlockLayout.addLayout(refAudioLayout)
        biliTtsBlockLayout.addLayout(refTextLayout)
        biliTtsBlockLayout.addLayout(refLangLayout)

        # ---- 保存按钮 & 状态 ----
        self._saveBtn = QPushButton("一键保存", self)
        self._saveBtn.clicked.connect(self.applySetting)
        self._settingStatus = QLabel("", self)
        self.setStatus("保存状态: 未保存", "#2563EB")

        mainLayout.addWidget(assetsBlock)
        mainLayout.addWidget(depsBlock)
        mainLayout.addWidget(biliBlock)
        mainLayout.addWidget(biliveBlock)
        mainLayout.addWidget(biliTtsBlock)
        mainLayout.addWidget(self._saveBtn)
        mainLayout.addWidget(self._settingStatus)
        mainLayout.addStretch()

    def onSelectImage(self):
        selectImagePath = QFileDialog.getOpenFileName(
            None,
            "选择图片或者GIF~",
            self._lastImageSelectDir,
            "图片文件 (*.png *.jpg *.gif *.jpeg *.webp)"
        )

        if selectImagePath[0] == "":
            return
        
        self._userAssetPath.setText(selectImagePath[0])
        self._lastImageSelectDir = str(pathlib.Path(selectImagePath[0]).parent)

    def onSelectFfmpeg(self):
        selectFfmpegPath = QFileDialog.getOpenFileName(
            None,
            "选择ffmpeg可执行文件~",
            self._lastFfmpegSelectDir,
            ""
        )

        if selectFfmpegPath[0] == "":
            return
        
        self._ffmpegPath.setText(selectFfmpegPath[0])
        self._lastFfmpegSelectDir = str(pathlib.Path(selectFfmpegPath[0]).parent)

    def setStatus(self, text: str, color: str):
        self._settingStatus.setText(text)
        self._settingStatus.setStyleSheet(
            f"color:{color};font-weight:bold;font-size:15px;"
        )

    @qasync.asyncSlot()
    async def applySetting(self):
        self._saveBtn.setEnabled(False)
        self.setStatus("保存状态: 保存中...", "#2563EB")

        if not pathlib.Path(self._userAssetPath.text()).exists():
            self.setStatus("保存状态: 保存失败~看板娘文件不存在~", "#B22222")
            self._saveBtn.setEnabled(True)
            
            return
        
        if self._userAssetPath.text() != config_loader.userConf.getImage():
            config_loader.userConf.saveImage(self._userAssetPath.text())

            self.changeCurrentImage.emit(self._userAssetPath.text())

        
        if not pathlib.Path(self._ffmpegPath.text()).exists():
            self.setStatus("保存状态: 保存失败~ffmpeg不存在~", "#B22222")
            self._saveBtn.setEnabled(True)
            
            return

        if self._ffmpegPath.text() != config_loader.userConf.getFfmpeg():
            config_loader.userConf.saveFfmpeg(self._ffmpegPath.text())

        config_loader.userConf.saveSessData(self._sessDataEdit.text()) 
        config_loader.userConf.saveBiliJct(self._biliJctEdit.text())
        config_loader.userConf.saveBuvid3(self._buvid3Edit.text())
            
        config_loader.userConf.saveLiveRoom(int(self._liveRoomId.text()))
            
        config_loader.userConf.setSovitsApiServer(self._apiServerEdit.text())

        gptOkToRequest : bool = self._gptModelEdit.text() != "" and self._gptModelEdit.text() != config_loader.userConf.getGptModel()
        sovitsOkToRequest : bool = self._sovitsModelEdit.text() != "" and self._sovitsModelEdit.text() != config_loader.userConf.getSovitsModel()

        modelsChangeResult : bool = False
        if gptOkToRequest or sovitsOkToRequest:
            async with aiohttp.ClientSession() as sess:
                modelsChangeResult = await sovits_http_helper.changeSpeaker(sess, self._gptModelEdit.text(), self._sovitsModelEdit.text())

        if gptOkToRequest or sovitsOkToRequest:
            if modelsChangeResult:
                config_loader.userConf.setGptModel(self._gptModelEdit.text())
                config_loader.userConf.setSovitsModel(self._sovitsModelEdit.text())
            else:
                self.setStatus("保存状态: 保存失败~GPT-SoVITS模型设置错误~", "#B22222")
                self._saveBtn.setEnabled(True)

                return

        config_loader.userConf.setRefAudio(self._refAudioEdit.text())
        config_loader.userConf.setRefAudioText(self._refTextEdit.text())
        config_loader.userConf.setRefAudioLang(self._refLangSelecter.itemData(self._refLangSelecter.currentIndex()))

        self.setStatus("保存状态: 保存成功!", "green")
        self._saveBtn.setEnabled(True)

    def closeEvent(self, event):
        config_loader.userConf.dumpUserConfig()
        
        self.readyToDestory.emit()
