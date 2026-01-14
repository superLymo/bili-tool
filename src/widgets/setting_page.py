from PySide6.QtWidgets import (
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox
)
# from utils import config_loader

class settingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self._init_ui()


    def _init_ui(self):
        mainLayout = QVBoxLayout(self)

        assetsBlock = QGroupBox("看板娘——可以是图片或者GIF~", self)
        assetsBlockLayout = QVBoxLayout(assetsBlock)

        self._userAssetPath = QLineEdit("", placeholderText="待选择...", parent=assetsBlock)
        self._userAssetPath.setEnabled(False)
        userAssetBtn = QPushButton("选择看板娘", assetsBlock)

        userAssetLayout = QHBoxLayout()
        userAssetLayout.addWidget(self._userAssetPath)
        userAssetLayout.addWidget(userAssetBtn)

        assetsBlockLayout.addLayout(userAssetLayout)


        depsBlock = QGroupBox("ffmpeg可执行文件路径", self)
        depsBlockLayout = QVBoxLayout(depsBlock)

        self._ffmpegPath = QLineEdit("", placeholderText="待选择...", parent=depsBlock)
        self._ffmpegPath.setEnabled(False)
        ffmpegBtn = QPushButton("选择Ffmpeg", depsBlock)

        ffmpegLayout = QHBoxLayout()
        ffmpegLayout.addWidget(self._ffmpegPath)
        ffmpegLayout.addWidget(ffmpegBtn)

        depsBlockLayout.addLayout(ffmpegLayout)


        biliBlock = QGroupBox("b站cookie配置", self)
        biliBlockLayout = QVBoxLayout(biliBlock)

        sessDataInfo = QLabel("SESSDATA: ", biliBlock)
        self._sessDataEdit = QLineEdit("", placeholderText="从浏览器获取的SESSDATA...", parent=biliBlock)

        sessDataLayout = QHBoxLayout()
        sessDataLayout.addWidget(sessDataInfo)
        sessDataLayout.addWidget(self._sessDataEdit)


        biliJctInfo = QLabel("bili_jct: ", biliBlock)
        self._biliJctEdit = QLineEdit("", placeholderText="从浏览器获取的bili_jct...", parent=biliBlock)

        biliJctLayout = QHBoxLayout()
        biliJctLayout.addWidget(biliJctInfo)
        biliJctLayout.addWidget(self._biliJctEdit)

        buvid3Info = QLabel("buvid3: ", biliBlock)
        self._buvid3Edit = QLineEdit("", placeholderText="从浏览器获取的buvid3...", parent=biliBlock)

        buvid3Layout = QHBoxLayout()
        buvid3Layout.addWidget(buvid3Info)
        buvid3Layout.addWidget(self._buvid3Edit)


        biliBlockLayout.addLayout(sessDataLayout)
        biliBlockLayout.addLayout(biliJctLayout)
        biliBlockLayout.addLayout(buvid3Layout)


        biliveBlock = QGroupBox("直播间配置", self)
        biliveBlockLayout = QVBoxLayout(biliveBlock)

        self._liveRoomId = QLineEdit("", placeholderText="8位数直播间号...", parent=biliveBlock)

        biliveBlockLayout.addWidget(self._liveRoomId)


        biliTtsBlock = QGroupBox("GPT-SoVITS配置", self)
        biliTtsBlockLayout = QVBoxLayout(biliTtsBlock)

        apiServerInfo = QLabel("api_v2地址: ", biliTtsBlock)
        self._apiServerEdit = QLineEdit("", biliTtsBlock, placeholderText=r"示例: http://127.0.0.1/9880")

        apiServerV2Layout = QHBoxLayout()
        apiServerV2Layout.addWidget(apiServerInfo)
        apiServerV2Layout.addWidget(self._apiServerEdit)


        gptModelInfo = QLabel("gpt模型路径: ", biliTtsBlock)
        self._gptModelEdit = QLineEdit("", biliTtsBlock, placeholderText="运行GPT-SoVITS的服务器上的路径...")

        gptModelLayout = QHBoxLayout()
        gptModelLayout.addWidget(gptModelInfo)
        gptModelLayout.addWidget(self._gptModelEdit)


        sovitsModelInfo = QLabel("sovits模型路径: ", biliTtsBlock)
        self._sovitsModelEdit = QLineEdit("", biliTtsBlock, placeholderText="运行GPT-SoVITS的服务器上的路径...")

        sovitsModelLayout = QHBoxLayout()
        sovitsModelLayout.addWidget(sovitsModelInfo)
        sovitsModelLayout.addWidget(self._sovitsModelEdit)

        refAudioInfo = QLabel("参考语音路径: ", biliTtsBlock)
        self._refAudioEdit = QLineEdit("", biliTtsBlock, placeholderText="运行GPT-SoVITS的服务器上的路径...")

        refAudioLayout = QHBoxLayout()
        refAudioLayout.addWidget(refAudioInfo)
        refAudioLayout.addWidget(self._refAudioEdit)


        refTextInfo = QLabel("参考文本内容: ", biliTtsBlock)
        self._refTextEdit = QLineEdit("", biliTtsBlock, placeholderText="参考语音里面的文本...")

        refTextLayout = QHBoxLayout()
        refTextLayout.addWidget(refTextInfo)
        refTextLayout.addWidget(self._refTextEdit)


        refLangInfo = QLabel("参考语音/文本的语言: ", biliTtsBlock)

        self._refLangSelecter = QComboBox(parent=biliTtsBlock)
        self._refLangSelecter.addItem("中文")
        self._refLangSelecter.setItemData(0, "zh")
        self._refLangSelecter.addItem("英语")
        self._refLangSelecter.setItemData(1, "en")
        self._refLangSelecter.addItem("日语")
        self._refLangSelecter.setItemData(2, "ja")
        self._refLangSelecter.addItem("韩语")
        self._refLangSelecter.setItemData(3, "ko")

        refLangLayout = QHBoxLayout()
        refLangLayout.addWidget(refLangInfo)
        refLangLayout.addWidget(self._refLangSelecter)

        biliTtsBlockLayout.addLayout(apiServerV2Layout)
        biliTtsBlockLayout.addLayout(gptModelLayout)
        biliTtsBlockLayout.addLayout(sovitsModelLayout)
        biliTtsBlockLayout.addLayout(refAudioLayout)
        biliTtsBlockLayout.addLayout(refTextLayout)
        biliTtsBlockLayout.addLayout(refLangLayout)


        saveBtn = QPushButton("一键保存", self)

        saveLayout = QHBoxLayout()
        saveLayout.addWidget(saveBtn)

        mainLayout.addWidget(assetsBlock)
        mainLayout.addWidget(depsBlock)
        mainLayout.addWidget(biliBlock)
        mainLayout.addWidget(biliveBlock)
        mainLayout.addWidget(biliTtsBlock)
        mainLayout.addLayout(saveLayout)

    def applySetting(self):

        
        pass

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = settingPage()
    window.show()
    sys.exit(app.exec())