# coding:utf-8
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem
from qfluentwidgets import FluentIcon, ListWidget, ScrollArea
from qfluentwidgets.common.icon import FluentIconEngine, Icon

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
        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(self.setWorkspace)
        GLOBAL_SIGNAL.dynamicModelUpdate.connect(self.updateList)

    def setWorkspace(self, workspace: Workspace):
        self.listWidget.clear()
        self._workspace = workspace
        for item in self._workspace.dynamics:
            dynamicsItem = QListWidgetItem(item.name)
            dynamicsItem.setIcon(QIcon(FluentIconEngine(Icon(FluentIcon.ROBOT))))
            self.listWidget.addItem(dynamicsItem)

    def updateList(self, name):
        """列表发生变化的时候进行更新

        Parameters
        ----------
        name : dtr
            添加的条目名称
        """
        self.listWidget.clear()
        _item = None
        for item in self._workspace.dynamics:
            dynamicsItem = QListWidgetItem(item.name)
            dynamicsItem.setIcon(QIcon(FluentIconEngine(Icon(FluentIcon.ROBOT))))
            self.listWidget.addItem(dynamicsItem)
            if name == item.name:
                _item = dynamicsItem
        if not _item == None:
            self.listWidget.scrollToItem(_item)
            self.listWidget.setCurrentItem(_item)
            self._itemClicked(_item)

    def _itemClicked(self, item: QListWidgetItem):
        for dynamicsModel in self._workspace.dynamics:
            if dynamicsModel.name == item.text():
                self.select_dynamicsModel = dynamicsModel
                break

        GLOBAL_SIGNAL.requestAddPage.emit(self.select_dynamicsModel.name, self._addpage)

    def _addpage(self, routeKey: str) -> BasePage:
        _page = DynamicsInformationPage(
            routeKey,
            self.select_dynamicsModel.name + " information",
            FluentIcon.ROBOT,
            self.select_dynamicsModel,
            0,
        )
        return _page
