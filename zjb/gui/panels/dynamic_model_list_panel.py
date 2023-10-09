# coding:utf-8
from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import ScrollArea, SubtitleLabel


class DynamicModelInterface(ScrollArea):
    """DynamicModelInterface 目录列表"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = SubtitleLabel("DynamicModelInterface")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.view)
        self.setObjectName("DynamicModelInterface")
        self.setStyleSheet("#DynamicModelInterface{background:transparent;border:none}")
