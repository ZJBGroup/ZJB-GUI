# coding:utf-8
from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import ScrollArea, SubtitleLabel


class DTBInterface(ScrollArea):
    """DTBInterface 树形结构"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = SubtitleLabel("DTBInterface")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.view)
        self.setObjectName("DTBInterface")
        self.setStyleSheet("#DTBInterface{background:transparent;border:none}")
