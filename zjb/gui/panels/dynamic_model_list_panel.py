# coding:utf-8
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem, QVBoxLayout
from qfluentwidgets import FluentIcon, ListWidget, ScrollArea
from zjb.main.manager.workspace import Workspace

from .._global import GLOBAL_SIGNAL


class DynamicModelInterface(ScrollArea):
    """DynamicModelInterface 目录列表"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._workspace = None
        self.listWidget = ListWidget(self)
        self.setObjectName("DynamicModelInterface")
        self.setStyleSheet("#DynamicModelInterface{background:transparent;border:none}")

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.listWidget)

        self.listWidget.itemClicked.connect(self._itemClicked)

    def setWorkspace(self, workspace: Workspace):
        self._workspace = workspace
        for item in self._workspace.dynamics:
            dynamicsItem = QListWidgetItem(item.name)
            dynamicsItem.setIcon(FluentIcon.ROBOT.icon())
            self.listWidget.addItem(dynamicsItem)

    def _itemClicked(self, item: QListWidgetItem):
        print("click:", item.text())
