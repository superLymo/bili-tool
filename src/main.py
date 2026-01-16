import sys
import asyncio
from PySide6.QtGui import QIcon
from qasync import QEventLoop, QApplication

from widgets.system_tray import biliTrayRegister
from widgets.animated_image_widget import AnimatedImageWidget
from utils import config_loader


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setApplicationName("哔哩哔哩小助手")
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(str(config_loader.userConf.getDefaultIco())))

    appCloseEvent = asyncio.Event()
    app.aboutToQuit.connect(appCloseEvent.set)

    widget = AnimatedImageWidget(str(config_loader.userConf.getImage()))

    sty = biliTrayRegister(app, widget, widget.showFromTray, app.quit)

    widget.show()

    asyncio.run(appCloseEvent.wait(), loop_factory=QEventLoop)
