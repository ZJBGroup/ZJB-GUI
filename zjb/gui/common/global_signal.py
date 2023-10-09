from PyQt5.QtCore import QObject, pyqtSignal


class GlobalSignal(QObject):
    jobUpdated = pyqtSignal()


GSIGNAL = GlobalSignal()
