# coding:utf-8
import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QWidget
from qfluentwidgets import (
    Action,
    FluentIcon,
    ListWidget,
    RoundMenu,
    TransparentDropDownPushButton,
)

from .._global import open_workspace
from ..common.config_path import get_local_config_path, sync_recent_config
from ..common.utils import show_error
from .input_name_dialog import show_dialog


class NewButton(TransparentDropDownPushButton):
    """New 按钮及其下拉菜单"""

    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.newMenu = RoundMenu(parent=self)
        self.newMenu.addAction(
            Action(FluentIcon.FOLDER_ADD, "WorkSpace", triggered=self._new_workspace)
        )
        self.newMenu.addAction(Action(FluentIcon.TILES, "Project"))
        self.newMenu.addAction(Action(FluentIcon.PEOPLE, "Subject"))
        self.newMenu.addAction(Action(FluentIcon.LIBRARY, "DTB Model"))
        self.newMenu.addAction(Action(FluentIcon.LEAF, "DTB"))
        self.setMenu(self.newMenu)

    def _new_workspace(self):
        """新建一个工作空间"""
        workspace_name = show_dialog(self.window())
        if workspace_name:
            w_path = QFileDialog.getExistingDirectory(self.window(), "New Workspace")
            if w_path:
                workspace_path = f"{w_path}/{workspace_name}"
                os.mkdir(workspace_path)
                sync_recent_config(workspace_name, workspace_path)
                open_workspace(workspace_path)


class OpenButton(TransparentDropDownPushButton):
    """Open 按钮及其下拉菜单"""

    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.openMenu = RoundMenu(parent=self)

        self.openMenu.addAction(
            Action(FluentIcon.FOLDER, "WorkSpace", triggered=self._open_workspace)
        )
        self.openMenu.addSeparator()

        self.recent_list = RecentWorkspaceList(self, "title")
        self.openMenu.addWidget(self.recent_list, selectable=False)

        self.openMenu.addSection("123")

        self.setMenu(self.openMenu)

    def _open_workspace(self):
        """打开一个工作空间"""
        workspace_path = QFileDialog.getExistingDirectory(
            self.window(), "Open Workspace"
        )
        if workspace_path:
            workspace_name = workspace_path.split("/")[
                len(workspace_path.split("/")) - 1
            ]
            get_worker_count = sync_recent_config(workspace_name, workspace_path)
            open_workspace(workspace_path)


class RecentWorkspaceItem(QListWidgetItem):
    """最近打开面板的每一个条目的类"""

    def __init__(self, obj, parent=None):
        super().__init__(parent)
        self.name = obj["name"]
        self.path = obj["path"]
        self.setText(f"{self.name} > {self.path}")

    def getWorkspacePath(self):
        """获取路径"""
        return self.path

    def getWorkspaceName(self):
        """获取名称"""
        return self.name


class RecentWorkspaceList(QWidget):
    """RecentList"""

    def __init__(self, parent=None, position="welcome"):
        super().__init__(parent=parent)
        self.listWidget = ListWidget(self)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        if position == "welcome":
            # 适用于欢迎页面的面板
            self.setMinimumWidth(320)
            self.listWidget.setMaximumHeight(85)
        else:
            # 适用于标题栏的面板
            self.setFixedSize(400, 150)
            self.listWidget.setFixedSize(360, 150)

        # 读取本地配置文件，取出最近打开过的工作区
        configPath = f"{get_local_config_path()}/recent_workspace.json"
        self.recentList = []
        # 若没有配置文件先创建一个
        if os.path.exists(configPath) == False:
            with open(configPath, "w") as f:
                data_str = json.dumps([])
                f.write(data_str)
        with open(configPath, "r") as f:
            self.recentList = json.load(f)
            for item in self.recentList:
                self.listWidget.addItem(RecentWorkspaceItem(item))
        self.listWidget.itemClicked.connect(self._on_current_item_click)

    def _on_current_item_click(self, item: RecentWorkspaceItem):
        """点击一个 最近打开 的条目"""
        w_path = item.getWorkspacePath()
        w_name = item.getWorkspaceName()
        if os.path.exists(w_path):
            get_worker_count = sync_recent_config(w_name, w_path)
            open_workspace(w_path)
        else:
            # 未找到文件
            sync_recent_config(w_name, w_path, state="del")
            show_error("workspace not find", self.window())
        self._sync_recent_list()
        self.listWidget.clearSelection()

    def _sync_recent_list(self):
        """每一次内容有修改之后更新整个 最近打开 的列表"""
        self.listWidget.clear()
        configPath = f"{get_local_config_path()}/recent_workspace.json"
        self.recentList = []
        with open(configPath, "r") as f:
            self.recentList = json.load(f)
        for item in self.recentList:
            self.listWidget.addItem(RecentWorkspaceItem(item))
