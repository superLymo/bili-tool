import sys, asyncio
from PySide6.QtGui import QIcon
from qasync import QEventLoop, QApplication

from widgets.system_tray import biliTrayRegister
from widgets.animated_image_widget import AnimatedImageWidget
from utils import config_loader


# 测试代码
if __name__ == "__main__":
    conf = config_loader.userConf

    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    app.setWindowIcon(QIcon(str(conf.getDefaultIco())))
    appCloseEvent = asyncio.Event()
    app.aboutToQuit.connect(appCloseEvent.set)

    widget = AnimatedImageWidget(str(conf.getImage()))

    sty = biliTrayRegister(app, widget, widget.showFromTray, app.quit)

    widget.show()

    asyncio.run(appCloseEvent.wait(), loop_factory=QEventLoop)
