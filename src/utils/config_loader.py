import pathlib
import tomllib
import tomli_w


class configLoader:
    def __init__(self):
        self._userConfig = None

        # 初始化和资源有关的默认路径常量
        self._projectPath = pathlib.Path(__file__).resolve().parent.parent.parent
        self._configPath = self._projectPath / r"user.toml"
        self._assetsPath = self._projectPath / r"assets"
        self._depsPath = self._projectPath / r"deps"

        self._defaultIco = self._assetsPath / r"app.ico"
        self._defaultStaticImage = self._assetsPath / r"angry.png"
        self._defaultAnimatedImage = self._assetsPath / r"smile.gif"

        if self._configPath.exists():
            self.loadUserConfig()
        else:
            self._genUserConfig()

    def loadUserConfig(self):
        with open(self._configPath, "rb") as f:
            self._userConfig = tomllib.load(f)

    def dumpUserConfig(self):
        with open(self._configPath, "wb") as f:
            tomli_w.dump(self._userConfig, f)

    def _genUserConfig(self):
        self._userConfig = {
            "assets": {"image": str(self._defaultAnimatedImage)},
            "deps": {"ffmpeg": ""},
            "bilibili": {
                "sessdata": "",
                "bili_jct": "",
                "buvid3": "",
                "live": {"room": ""},
            },
            "sovits": {
                "api_server": "",
                "gpt_model_path": "",
                "sovits_model_path": "",
                "ref_audio_path": "",
                "ref_audio_text": "",
                "ref_audio_lang": "",
            },
        }

        self.dumpUserConfig()

    def getProjectPath(self):
        return self._projectPath

    def getUserConfigPath(self):
        return self._configPath

    def getAssetsPath(self):
        return self._assetsPath

    def getDepsPath(self):
        return self._depsPath

    def getDefaultIco(self):
        return self._defaultIco

    def getDefaultStaticImage(self):
        return self._defaultStaticImage

    def getDefaultAnimatedImage(self):
        return self._defaultAnimatedImage

    def getImage(self) -> str:
        if not pathlib.Path(self._userConfig["assets"]["image"]).exists():
            self.saveImage(str(self.getDefaultAnimatedImage()))

        return self._userConfig["assets"]["image"]

    def saveImage(self, path: str):
        self._userConfig["assets"]["image"] = path

    def getFfmpeg(self) -> str:
        return self._userConfig["deps"]["ffmpeg"]

    def saveFfmpeg(self, path: str):
        self._userConfig["deps"]["ffmpeg"] = path

    def getSessData(self) -> str:
        return self._userConfig["bilibili"]["sessdata"]

    def saveSessData(self, sessdata: str):
        self._userConfig["bilibili"]["sessdata"] = sessdata

    def getBiliJct(self) -> str:
        return self._userConfig["bilibili"]["bili_jct"]

    def saveBiliJct(self, bili_jct: str):
        self._userConfig["bilibili"]["bili_jct"] = bili_jct

    def getBuvid3(self) -> str:
        return self._userConfig["bilibili"]["buvid3"]

    def saveBuvid3(self, buvid3: str):
        self._userConfig["bilibili"]["buvid3"] = buvid3

    def getLiveRoom(self):
        return int(self._userConfig["bilibili"]["live"]["room"])

    def saveLiveRoom(self, roomId: int) -> None:
        self._userConfig["bilibili"]["live"]["room"] = str(roomId)

    def getSovitsApiServer(self) -> str:
        return self._userConfig["sovits"]["api_server"]

    def setSovitsApiServer(self, serverUrl: str):
        self._userConfig["sovits"]["api_server"] = serverUrl

    def getGptModel(self) -> str:
        return self._userConfig["sovits"]["gpt_model_path"]

    def setGptModel(self, newGptModelPath: str):
        self._userConfig["sovits"]["gpt_model_path"] = newGptModelPath

    def getSovitsModel(self) -> str:
        return self._userConfig["sovits"]["sovits_model_path"]

    def setSovitsModel(self, newSovitsModelPath: str):
        self._userConfig["sovits"]["sovits_model_path"] = newSovitsModelPath

    def getRefAudio(self) -> str:
        return self._userConfig["sovits"]["ref_audio_path"]

    def setRefAudio(self, newAudioPath: str):
        self._userConfig["sovits"]["ref_audio_path"] = newAudioPath

    def getRefAudioText(self) -> str:
        return self._userConfig["sovits"]["ref_audio_text"]

    def setRefAudioText(self, newText: str):
        self._userConfig["sovits"]["ref_audio_text"] = newText

    def getRefAudioLang(self) -> str:
        return self._userConfig["sovits"]["ref_audio_lang"]

    def setRefAudioLang(self, newLang: str):
        self._userConfig["sovits"]["ref_audio_lang"] = newLang


userConf = configLoader()
