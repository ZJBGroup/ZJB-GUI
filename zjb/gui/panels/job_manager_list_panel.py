# coding:utf-8
from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import ScrollArea, SubtitleLabel


class JobManagerInterface(ScrollArea):
    """JobManagerInterface 目录列表"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = SubtitleLabel("JobManagerInterface")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.view)
        self.setObjectName("JobManagerInterface")
        self.setStyleSheet("#JobManagerInterface{background:transparent;border:none}")
