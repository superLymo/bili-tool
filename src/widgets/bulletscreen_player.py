from typing import Optional
from dataclasses import dataclass
import datetime
import asyncio
import aiohttp
import qasync
import nava
from PySide6.QtCore import QObject, Signal
from core import blivedm_signal
from utils import config_loader
from utils import sovits_http_helper


@dataclass
class wavMeta:
    data: Optional[bytes]
    available: bool


class bulletscreenObject(QObject):
    startRunning = Signal()
    stopRunning = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._session: Optional[aiohttp.ClientSession] = None
        self._wavQueue = asyncio.Queue()

    def runPlayer(self):
        if self._session:
            return

        self._session = aiohttp.ClientSession()

        blivedm_signal.bldmEmitter.messageLoaded.connect(self.onMsgHere)

        self.wayPlayAsync()

    @qasync.asyncSlot()
    async def onMsgHere(self, prefix : str, msg: str) -> None:
        try:
            finalText = prefix + msg
            textLang = self.detectLanguages(finalText)

            jsonToPost = sovits_http_helper.genTtsPostJson(finalText, textLang)

            async with self._session.post(
                config_loader.userConf.getSovitsApiServer() + "/tts",
                json=jsonToPost,
            ) as resp:
                if resp.status != 200:
                    return

                wavData = await resp.read()

                await self._wavQueue.put(wavMeta(wavData, True))
        except Exception as e:
            print(f"tts的post请求失败了: {e}")

    def wavPlaySync(self, wavData: wavMeta):
        tempDir = config_loader.userConf.getProjectPath() / "temp"

        if not tempDir.exists():
            tempDir.mkdir(parents=True, exist_ok=True)

        wavFilePath = tempDir / f"{int(datetime.datetime.now().timestamp())}.wav"

        with open(wavFilePath, "wb") as f:
            f.write(wavData.data)

        try:
            nava.play(str(wavFilePath))
        except Exception as e:
            print(f"nava play failed with {e}")
        finally:
            wavFilePath.unlink(missing_ok=True)

    @qasync.asyncSlot()
    async def wayPlayAsync(self):
        self.startRunning.emit()

        while self._session:
            wavData: wavMeta = await self._wavQueue.get()

            if not wavData.available:
                self._wavQueue.task_done()

                break

            await asyncio.to_thread(self.wavPlaySync, wavData)

            self._wavQueue.task_done()

        while not self._wavQueue.empty():
            try:
                self._wavQueue.get_nowait()
                self._wavQueue.task_done()
            finally:
                pass

        self.stopRunning.emit()

    def stopPlayer(self):
        if not self._session:
            return

        blivedm_signal.bldmEmitter.messageLoaded.disconnect(self.onMsgHere)

        self._cleanSession()

    @qasync.asyncSlot()
    async def _cleanSession(self):
        await self._session.close()
        await self._wavQueue.put(wavMeta(None, False))

        self._session = None

    def isRunning(self) -> bool :
        return self._session is not None

    def detectLanguages(self, text: str) -> str:
        # 位标志：第0位=中文，第1位=日文，第2位=韩文，第3位=英文
        flags = 0b0000
        
        for ch in text:
            code = ord(ch)
            
            # 使用位运算加速
            if not (flags & 0b0001) and (19968 <= code <= 40959): 
                flags |= 0b0001  # 设置中文位
            elif not (flags & 0b0010) and (12352 <= code <= 12543): 
                flags |= 0b0010  # 设置日文位
            elif not (flags & 0b1000) and ((65 <= code <= 90) or (97 <= code <= 122)):  
                flags |= 0b1000  # 设置英文位
            elif not (flags & 0b0100) and (44032 <= code <= 55203):  
                flags |= 0b0100  # 设置韩文位
            
            # 如果所有位都已设置，提前退出
            if flags == 0b1111:
                break
        
        # 预定义的查找表：位标志 -> 返回代码
        RESULT_MAP = {
            # 纯语言（只有1位为1）
            0b0001: "all_zh",  # 只有中文
            0b0010: "all_ja",  # 只有日文
            0b0100: "all_ko",  # 只有韩文
            0b1000: "en",      # 只有英文
            
            # 中英混合（中文+英文）
            0b1001: "zh",      # 中文(0001) + 英文(1000) = 1001
            
            # 日英混合（日文+英文）
            0b1010: "ja",      # 日文(0010) + 英文(1000) = 1010
            
            # 韩英混合（韩文+英文）
            0b1100: "ko",      # 韩文(0100) + 英文(1000) = 1100
            
            # 默认：其他所有混合情况
        }
        
        # 查找结果（O(1)时间复杂度）
        return RESULT_MAP.get(flags, "auto")