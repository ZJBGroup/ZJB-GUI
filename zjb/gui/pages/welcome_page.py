import json
import os
from threading import Thread

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMovie
from qfluentwidgets import FluentIcon, ListWidget
from zjb.main.manager.workspace import Workspace

from .._global import GLOBAL_SIGNAL, open_workspace
from ..common.config import cfg
from ..common.config_path import get_local_config_path, sync_recent_config
from ..common.download_file import DownLoadFile
from ..common.utils import show_error
from ..common.zjb_style_sheet import myZJBStyleSheet
from ..widgets.input_name_dialog import show_dialog
from .base_page import BasePage


class StartPanel(QtWidgets.QWidget):
    """主页开始面板"""

    def __init__(self, text: str, worker_count, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QtWidgets.QHBoxLayout(self)
        self._worker_count = worker_count
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
        self.newWorkspace.setIcon(FluentIcon.FOLDER_ADD.icon())
        self.listWidget.addItem(self.newWorkspace)
        self.openWorkspace = QtWidgets.QListWidgetItem("Open Workspace")
        self.openWorkspace.setIcon(FluentIcon.FOLDER.icon())
        self.listWidget.addItem(self.openWorkspace)
        self.right_panel_layout.addWidget(self.listWidget)
        self.right_panel.setMaximumWidth(200)
        self.listWidget.setMaximumWidth(200)
        self.listWidget.itemClicked.connect(self._on_current_item_click)
        # 增加布局
        self.hBoxLayout.addWidget(self.left_panel)
        self.hBoxLayout.addWidget(self.right_panel)
        cfg.themeChanged.connect(lambda: self._sync_listWidget())

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
        workspace_name = show_dialog(self.window())
        if workspace_name:
            w_path = QtWidgets.QFileDialog.getExistingDirectory(self, "New Workspace")
            if w_path:
                workspace_path = f"{w_path}/{workspace_name}"
                os.mkdir(workspace_path)
                sync_recent_config(workspace_name, workspace_path)
                open_workspace(workspace_path)

    def _open_workspace(self):
        """打开一个工作空间"""
        workspace_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Open Workspace"
        )
        if workspace_path:
            workspace_name = workspace_path.split("/")[
                len(workspace_path.split("/")) - 1
            ]
            get_worker_count = sync_recent_config(workspace_name, workspace_path)
            open_workspace(workspace_path)

    def _sync_listWidget(self):
        """主要用于主题修改之后，刷新一下列表更新图标的颜色"""
        self.listWidget.clear()
        self.listWidget.clearSelection()
        self.newWorkspace = QtWidgets.QListWidgetItem("New Workspace")
        self.newWorkspace.setIcon(FluentIcon.FOLDER_ADD.icon())
        self.listWidget.addItem(self.newWorkspace)
        self.openWorkspace = QtWidgets.QListWidgetItem("Open Workspace")
        self.openWorkspace.setIcon(FluentIcon.FOLDER.icon())
        self.listWidget.addItem(self.openWorkspace)


class RecentWorkspaceItem(QtWidgets.QListWidgetItem):
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


class RecentPanel(QtWidgets.QWidget):
    """最近打开模块的面板类"""

    def __init__(self, text: str, worker_count, parent=None):
        super().__init__(parent)
        self._worker_count = worker_count
        self.hBoxLayout = QtWidgets.QHBoxLayout(self)
        # 左侧 RECENT label
        self.left_panel = QtWidgets.QWidget(self)
        self.left_panel.setMaximumWidth(200)
        self.left_panel_layout = QtWidgets.QVBoxLayout(self.left_panel)
        self.setObjectName(text.replace(" ", "_"))
        self.labelTitle = QtWidgets.QLabel("RECENT", self)
        self.labelTitle.setObjectName("labelTitle")
        self.left_panel_layout.addWidget(self.labelTitle)
        myZJBStyleSheet.SETTING_STYLE.apply(self)
        # 右侧列表
        self.right_panel = QtWidgets.QWidget(self)
        self.right_panel.setMinimumWidth(300)
        self.right_panel_layout = QtWidgets.QVBoxLayout(self.right_panel)
        self.listWidget = ListWidget(self)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        self.right_panel_layout.addWidget(self.listWidget)
        self.listWidget.itemClicked.connect(self._on_current_item_click)
        # 增加布局
        self.hBoxLayout.addWidget(self.left_panel)
        self.hBoxLayout.addWidget(self.right_panel)

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
        # 异步下载首页gif动图
        configPath = f"{get_local_config_path()}/BNA_V2.gif"
        down_url = "http://10.11.140.13:8000/f/45b1fd709a964665827a/?dl=1"  # BNA_V2.gif
        downobj = DownLoadFile(down_url, configPath)
        downobj._downLoadFinished.connect(lambda: self.load_gif(configPath))
        t = Thread(target=downobj.download_from_url, daemon=True)
        t.start()
        if os.path.exists(configPath):
            self.load_gif(configPath)
        else:
            self.loading()
        # 获取本机CPU核数，结合配置文件 配置默认的 Worker 数量
        default_count = 5
        worker_count = (
            default_count if os.cpu_count() > default_count else os.cpu_count()
        )
        # 操作区板块
        self.bottom_panel = QtWidgets.QWidget(self)
        self.bottom_panel.setMaximumHeight(120)
        self.bottom_panel.setMinimumHeight(120)
        self.bottom_panel.setObjectName("bottom_panel")
        self.bottom_panel_layout = QtWidgets.QHBoxLayout(self.bottom_panel)
        self.bottom_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_panel_layout.setObjectName("bottom_panel_layout")
        self.bottom_left_panel_layout = StartPanel("left", worker_count, self)
        self.bottom_left_panel_layout.setObjectName("bottom_left_panel_layout")
        self.bottom_right_panel_layout = RecentPanel("right", worker_count, self)
        self.bottom_right_panel_layout.setObjectName("bottom_right_panel_layout")
        self.bottom_panel_layout.addStretch(3)
        self.bottom_panel_layout.addWidget(self.bottom_left_panel_layout)
        self.bottom_panel_layout.addStretch(1)
        self.bottom_panel_layout.addWidget(self.bottom_right_panel_layout)
        self.bottom_panel_layout.addStretch(3)
        self.vBoxLayout.addWidget(self.bottom_panel)
        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(
            self.bottom_right_panel_layout._sync_recent_list
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
        self.gif_label.setMaximumSize(QSize(700, 383))
        self.movie.start()
        self.gif_label.setScaledContents(True)
        self.setStyleSheet(
            "QLabel#gif_label{padding:0 30;background:rgba(0,0,0,1);border-radius:30;}"
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
                self.scalebase["width"] * temp - 127
                if self.scalebase["width"] * temp - 127 > 700
                else 700
            )
            new_height = (
                self.scalebase["height"] * temp - 211
                if self.scalebase["height"] * temp - 211 > 383
                else 383
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

    def loading(self):
        """gif图板块显示 加载中的 样式"""
        self.gif_label.setText("图片加载中......")
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "QLabel#gif_label{font: 30px 'Microsoft YaHei Light';background:rgba(0,0,0,0.6);border-radius:20;color:white}"
        )
