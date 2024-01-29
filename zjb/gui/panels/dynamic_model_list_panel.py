# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem
from qfluentwidgets import Action, FluentIcon, ListWidget, RoundMenu, ScrollArea
from qfluentwidgets.common.icon import FluentIconEngine, Icon

from zjb.main.manager.workspace import Workspace

from .._global import GLOBAL_SIGNAL
from ..pages.base_page import BasePage
from ..pages.dynamics_page import DynamicsInformationPage
from ..pages.new_dynamics_page import NewDynamicsPage


class DynamicModelInterface(ScrollArea):
    """DynamicModelInterface 目录列表"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._workspace = None
        self._window = parent
        self.listWidget = ListWidget(self)
        self.setObjectName("DynamicModelInterface")
        self.setStyleSheet("#DynamicModelInterface{background:transparent;border:none}")

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.listWidget)

        self.listWidget.itemClicked.connect(self._itemClicked)
        self.listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self._show_context_menu)
        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(self.setWorkspace)
        GLOBAL_SIGNAL.dynamicModelUpdate.connect(self.updateList)  # 删除和添加的时候刷新列表

    def setWorkspace(self, workspace: Workspace):
        self.listWidget.clear()
        self._workspace = workspace
        for item in self._workspace.dynamics:
            dynamicsItem = QListWidgetItem(item.name)
            dynamicsItem.setIcon(QIcon(FluentIconEngine(Icon(FluentIcon.ROBOT))))
            self.listWidget.addItem(dynamicsItem)

    def updateList(self, name="", type=""):
        """列表发生变化的时候进行更新

        Parameters
        ----------
        name : str
            添加的条目名称
        """
        if type == "delete" or type == "create":
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

    def _show_context_menu(self, pos):
        """右键点击一个条目时，触发右键菜单"""
        self.rightClickItem = self.listWidget.itemAt(pos)
        self.listWidget.setCurrentItem(self.rightClickItem)
        rightMenu = RoundMenu()
        copy_action = Action(
            FluentIcon.COPY,
            "Copy",
            triggered=self.copy_dynamic,
        )
        delete_action = Action(
            FluentIcon.DELETE,
            "Delete",
            triggered=self.delete_dynamic,
        )
        rightMenu.addAction(copy_action)
        rightMenu.addAction(delete_action)
        rightMenu.exec(self.listWidget.mapToGlobal(pos))

    def copy_dynamic(self):
        """右键复制 dynamic model"""
        GLOBAL_SIGNAL.dynamicModelUpdate.emit(
            "New Dynamic Model", "copy"
        )  # 先关掉已打开的编辑页面
        GLOBAL_SIGNAL.requestAddPage.emit(
            "New Dynamic Model",
            lambda _: NewDynamicsPage(
                "New Dynamic Model", self.listWidget.currentItem().text(), self._window
            ),
        )

    def delete_dynamic(self):
        """右键删除 dynamic model"""
        model_name = self.listWidget.currentItem().text()
        for dynamicsModel in self._workspace.dynamics:
            if dynamicsModel.name == model_name:
                self.select_dynamicsModel = dynamicsModel
                break
        _dynamics = self._workspace.dynamics
        _dynamics.remove(self.select_dynamicsModel)
        self._workspace.dynamics = _dynamics
        GLOBAL_SIGNAL.dynamicModelUpdate.emit(model_name, "delete")
        # self.updateList()

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
