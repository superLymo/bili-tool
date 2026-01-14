from typing import Optional
import aiohttp
import http.cookies
import blivedm
from core import blivedm_handler
from PySide6.QtCore import QObject
import qasync
from utils import config_loader


class blivedmObject(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._blClient: Optional[blivedm.BLiveClient] = None

    @qasync.asyncSlot()
    async def runBlivedm(self):
        if not self._blClient:
            await self._runBlivedm()

    @qasync.asyncSlot()
    async def _runBlivedm(self):
        cks = http.cookies.SimpleCookie()
        cks["SESSDATA"] = config_loader.userConf.getSessData()
        cks["SESSDATA"]["domain"] = "bilibili.com"

        async with aiohttp.ClientSession(cookies=cks) as cliSess:
            self._blClient = blivedm.BLiveClient(
                config_loader.userConf.getLiveRoom(), session=cliSess
            )
            self._blClient.set_handler(blivedm_handler.blivedmHandler())

            self._blClient.start()

            try:
                await self._blClient.join()
            finally:
                await self._blClient.stop_and_close()
                self._blClient = None

    def stopBlivedm(self):
        if self._blClient:
            self._blClient.stop()
