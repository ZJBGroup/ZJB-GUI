# coding:utf-8
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem, QVBoxLayout
from qfluentwidgets import FluentIcon, ListWidget, ScrollArea

from zjb.main.manager.workspace import Workspace

from .._global import GLOBAL_SIGNAL
from ..pages.base_page import BasePage
from ..pages.dynamics_page import DynamicsInformationPage


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
        for dynamicsModel in self._workspace.dynamics:
            if dynamicsModel.name == item.text():
                self.select_dynamicsModel = dynamicsModel
                break

        GLOBAL_SIGNAL.requestAddPage.emit(self.select_dynamicsModel.name, self._addpage)

    def _addpage(self, routeKey: str) -> BasePage:
        _page = DynamicsInformationPage(
            routeKey,
            self.select_dynamicsModel.name + "information",
            FluentIcon.DEVELOPER_TOOLS,
            self.select_dynamicsModel,
            0,
        )
        return _page
