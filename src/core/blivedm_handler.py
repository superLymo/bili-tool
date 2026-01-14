import blivedm
import blivedm.models.web as webModels
from core import blivedm_signal


class blivedmHandler(blivedm.BaseHandler):
    def __init__(self):
        super().__init__()

    def _on_heartbeat(
        self, client: blivedm.BLiveClient, message: webModels.HeartbeatMessage
    ):
        dmToSend: str = f"{client.room_id}的心跳包"

        # blivedm_signal.bldmEmitter.messageLoaded.emit(dmToSend)

        print(dmToSend)

        pass

    def _on_danmaku(
        self, client: blivedm.BLiveClient, message: webModels.DanmakuMessage
    ):
        dmToSend: str = f"{message.uname}说: {message.msg}"

        blivedm_signal.bldmEmitter.messageLoaded.emit(dmToSend)

        # print(dmToSend)

        pass

    def _on_super_chat(
        self, client: blivedm.BLiveClient, message: webModels.SuperChatMessage
    ):
        dmToSend: str = (
            f"{message.uname}通过{message.price}元醒目留言说: {message.message}"
        )

        blivedm_signal.bldmEmitter.messageLoaded.emit(dmToSend)

        # print(dmToSend)

        pass

    def _on_gift(self, client: blivedm.BLiveClient, message: webModels.GiftMessage):
        dmToSend: str = f"{message.uname}送出{message.num}个{message.gift_name}！"

        blivedm_signal.bldmEmitter.messageLoaded.emit(dmToSend)

        # print(dmToSend)

        pass

    def _on_user_toast_v2(
        self, client: blivedm.BLiveClient, message: webModels.UserToastV2Message
    ):
        if message.source == 2:
            return

        currentLevelName: str = "没上舰"

        match message.guard_level:
            case 1:
                currentLevelName = "总督"
            case 2:
                currentLevelName = "提督"
            case 3:
                currentLevelName = "舰长"

        dmToSend: str = f"{message.username}成功上舰！成为了{currentLevelName}！"

        blivedm_signal.bldmEmitter.messageLoaded.emit(dmToSend)

        # print(dmToSend)

        pass

    def _on_interact_word_v2(
        self, client: blivedm.BLiveClient, message: webModels.InteractWordV2Message
    ):
        pass
