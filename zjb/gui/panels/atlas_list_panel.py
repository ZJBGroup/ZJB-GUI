# coding:utf-8
from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import ScrollArea, SubtitleLabel


class AtlasInterface(ScrollArea):
    """AtlasInterface 目录列表"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = SubtitleLabel("AtlasInterface")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.view)
        self.setObjectName("AtlasInterface")
        self.setStyleSheet("#AtlasInterface{background:transparent;border:none}")
