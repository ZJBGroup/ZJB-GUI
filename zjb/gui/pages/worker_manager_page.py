from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from qfluentwidgets import IconWidget, SubtitleLabel

from .base_page import BasePage


class WorkerManagerPage(BasePage):
    """Tab interface"""

    def __init__(self, routeKey: str, title: str, icon, parent=None):
        super().__init__(routeKey, title, icon, parent)
        self.iconWidget = IconWidget(icon, self)
        self.label = SubtitleLabel(routeKey, self)
        self.iconWidget.setFixedSize(120, 120)

        self.vBoxLayout = QtWidgets.QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignCenter)

        self.setObjectName(routeKey)
