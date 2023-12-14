import os
from enum import IntEnum

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QMovie
from qfluentwidgets import FluentIcon, ListWidget
from qfluentwidgets.common.icon import FluentIconEngine, Icon

from zjb.gui.assets import get_asset_path
from zjb.main.api import Workspace

from .._global import GLOBAL_SIGNAL, open_workspace
from ..common.config_path import sync_recent_config
from ..common.utils import show_success
from ..common.zjb_style_sheet import myZJBStyleSheet
from ..widgets.input_name_dialog import dialog_workspace
from ..widgets.titlebar_button import RecentWorkspaceList
from .base_page import BasePage


class GifBaseSize(IntEnum):
    WIDTH = 800
    HEIGHT = 437


class StartPanel(QtWidgets.QWidget):
    """主页开始面板"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.hBoxLayout = QtWidgets.QHBoxLayout(self)
        # 左侧 start label
        self.left_panel = QtWidgets.QWidget(self)
        self.left_panel.setMaximumWidth(200)
        self.left_panel_layout = QtWidgets.QVBoxLayout(self.left_panel)
        self.setObjectName(text.replace(" ", "_"))
        self.labelTitle = QtWidgets.QLabel("START", self)
        self.labelTitle.setObjectName("labelTitle")
        self.left_panel_layout.addWidget(self.labelTitle)
        myZJBStyleSheet.SETTING_STYLE.apply(self)
        # 右侧两个功能键
        self.right_panel = QtWidgets.QWidget(self)
        self.right_panel_layout = QtWidgets.QVBoxLayout(self.right_panel)
        self.listWidget = ListWidget(self)
        self.newWorkspace = QtWidgets.QListWidgetItem("New Workspace")
        self.newWorkspace.setIcon(QIcon(FluentIconEngine(Icon(FluentIcon.FOLDER_ADD))))
        self.listWidget.addItem(self.newWorkspace)
        self.openWorkspace = QtWidgets.QListWidgetItem("Open Workspace")
        self.openWorkspace.setIcon(QIcon(FluentIconEngine(Icon(FluentIcon.FOLDER))))
        self.listWidget.addItem(self.openWorkspace)
        self.right_panel_layout.addWidget(self.listWidget)
        self.right_panel.setMaximumWidth(200)
        self.listWidget.setMaximumWidth(200)
        self.listWidget.itemClicked.connect(self._on_current_item_click)
        # 增加布局
        self.hBoxLayout.addWidget(self.left_panel)
        self.hBoxLayout.addWidget(self.right_panel)

    def _on_current_item_click(self, item: QtWidgets.QListWidgetItem):
        """
        点击按钮触发不同的事件
        :param: item: 所点击的条目
        """
        if item.text() == "New Workspace":
            self._new_workspace()
        if item.text() == "Open Workspace":
            self._open_workspace()
        self.listWidget.clearSelection()

    def _new_workspace(self):
        """新建一个工作空间"""
        workspace_name = dialog_workspace(parent=self.window())
        if workspace_name == "canel":
            return
        elif not workspace_name == False:
            w_path = QtWidgets.QFileDialog.getExistingDirectory(
                self.window(), "New Workspace"
            )
            if w_path:
                workspace_path = f"{w_path}/{workspace_name}"
                os.mkdir(workspace_path)
                sync_recent_config(workspace_name, workspace_path)
                open_workspace(workspace_path)
                show_success(
                    f"Successfully opened workspace {workspace_name}", self._parent
                )

    def _open_workspace(self):
        """打开一个工作空间"""
        workspace_path = QtWidgets.QFileDialog.getExistingDirectory(
            self.window(), "Open Workspace"
        )
        if workspace_path:
            workspace_name = workspace_path.split("/")[
                len(workspace_path.split("/")) - 1
            ]
            get_worker_count = sync_recent_config(workspace_name, workspace_path)
            open_workspace(workspace_path, get_worker_count)
            show_success(
                f"Successfully opened workspace {workspace_name}", self._parent
            )


class RecentPanel(QtWidgets.QWidget):
    """最近打开模块的面板类"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QtWidgets.QHBoxLayout(self)
        self.left_panel = QtWidgets.QWidget(self)
        self.left_panel.setMaximumWidth(200)
        self.left_panel_layout = QtWidgets.QVBoxLayout(self.left_panel)
        self.setObjectName(text.replace(" ", "_"))
        self.labelTitle = QtWidgets.QLabel("RECENT", self)
        self.labelTitle.setObjectName("labelTitle")
        self.left_panel_layout.addWidget(self.labelTitle)
        myZJBStyleSheet.SETTING_STYLE.apply(self)
        self.right_panel = RecentWorkspaceList(position="welcome", parent=parent)
        self.hBoxLayout.addWidget(self.left_panel)
        self.hBoxLayout.addWidget(self.right_panel)


class WelcomePage(BasePage):
    def __init__(self, routeKey: str, title: str, icon, parent=None):
        super().__init__(routeKey, title, icon, parent)
        self.setObjectName(routeKey)
        self.vBoxLayout = QtWidgets.QVBoxLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
        # 添加gif图的板块
        self.top_panel = QtWidgets.QWidget(self)
        self.top_panel.setObjectName("top_panel")
        self.top_panel_layout = QtWidgets.QVBoxLayout(self.top_panel)
        self.top_panel_layout.setAlignment(Qt.AlignCenter)
        self.gif_label = QtWidgets.QLabel("", self.top_panel)
        self.gif_label.setObjectName("gif_label")
        self.top_panel_layout.addWidget(self.gif_label)
        self.vBoxLayout.addWidget(self.top_panel)

        # self.load_gif(find_resource_file("images/welcome.gif"))
        self.load_gif(get_asset_path("images/welcome.gif"))

        # 操作区板块
        self.bottom_panel = QtWidgets.QWidget(self)
        self.bottom_panel.setMaximumHeight(120)
        self.bottom_panel.setMinimumHeight(120)
        self.bottom_panel.setObjectName("bottom_panel")
        self.bottom_panel_layout = QtWidgets.QHBoxLayout(self.bottom_panel)
        self.bottom_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_panel_layout.setObjectName("bottom_panel_layout")
        self.bottom_left_panel_layout = StartPanel("left", parent)
        self.bottom_left_panel_layout.setObjectName("bottom_left_panel_layout")
        self.bottom_right_panel_layout = RecentPanel("right", parent)
        self.bottom_right_panel_layout.setObjectName("bottom_right_panel_layout")
        self.bottom_panel_layout.addStretch(3)
        self.bottom_panel_layout.addWidget(self.bottom_left_panel_layout)
        self.bottom_panel_layout.addStretch(1)
        self.bottom_panel_layout.addWidget(self.bottom_right_panel_layout)
        self.bottom_panel_layout.addStretch(3)
        self.vBoxLayout.addStretch()
        self.vBoxLayout.addWidget(self.bottom_panel)

        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(
            self.bottom_right_panel_layout.right_panel._sync_recent_list
        )
        self.scalebase = {"width": 11, "height": 7}

    def load_gif(self, configPath):
        """
        调用方法加载本地的gif图
        :param: configPath: gif的路径
        """
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie(configPath)
        self.gif_label.setMovie(self.movie)
        self.gif_label.setMaximumSize(QSize(GifBaseSize.WIDTH, GifBaseSize.HEIGHT))
        self.movie.start()
        self.gif_label.setScaledContents(True)
        self.setStyleSheet(
            "QLabel#gif_label{padding:0 30;background:rgba(0,0,0,1);border-radius:0;}"
        )

    def resizeEvent(self, QResizeEvent):
        """
        当窗口大小变化时，调整 gif 图片等比缩放
        :param: QResizeEvent: gif的路径
        """
        scale = 1.83
        temp = 100
        if (
            not QResizeEvent.size().width() // 100 == self.scalebase["width"]
            or not QResizeEvent.size().height() // 100 == self.scalebase["height"]
        ):
            self.scalebase["width"] = QResizeEvent.size().width() // 100
            self.scalebase["height"] = QResizeEvent.size().height() // 100
            new_width = (
                self.scalebase["width"] * temp
                if self.scalebase["width"] * temp > GifBaseSize.WIDTH
                else GifBaseSize.WIDTH
            )
            new_height = (
                self.scalebase["height"] * temp
                if self.scalebase["height"] * temp > GifBaseSize.HEIGHT
                else GifBaseSize.HEIGHT
            )
            if new_width / new_height > scale:
                self.gif_label.setMaximumWidth(int(scale * new_height))
                self.gif_label.setMinimumWidth(int(scale * new_height))
                self.gif_label.setMaximumHeight(new_height)
                self.gif_label.setMinimumHeight(new_height)
            else:
                self.gif_label.setMaximumWidth(new_width)
                self.gif_label.setMinimumWidth(new_width)
                self.gif_label.setMaximumHeight(int(new_width / scale))
                self.gif_label.setMinimumHeight(int(new_width / scale))
