from PySide6.QtCore import QObject, Signal


class blivedmSignals(QObject):
    messageLoaded = Signal(str)


bldmEmitter = blivedmSignals()
