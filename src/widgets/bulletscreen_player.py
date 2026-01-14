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
    async def onMsgHere(self, msg: str) -> None:
        try:
            jsonToPost = sovits_http_helper.genTtsPostJson(msg)

            async with self._session.post(
                config_loader.userConf.getSovitsApiServer() + "/tts",
                json=jsonToPost,
            ) as resp:
                if resp.status != 200:
                    return

                wavData = await resp.read()

                await self._wavQueue.put(wavMeta(wavData, True))
        finally:
            pass

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
