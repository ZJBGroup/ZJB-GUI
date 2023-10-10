import json
import os
import re
import typing
from threading import Thread

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QMovie
from qfluentwidgets import CaptionLabel, Dialog, FluentIcon, LineEdit, ListWidget

from ..common.config import cfg
from ..common.config_path import get_local_config_path, sync_recent_config
from ..common.download_file import DownLoadFile
from ..common.utils import show_error
from ..common.zjb_style_sheet import myZJBStyleSheet
from .base_page import BasePage


class Workspace:
    def __init__(self, path: str, worker_count, parent=None):
        self._worker_count = worker_count
        self._path = path


class InputDialog(Dialog):
    """输入工作空间名称的弹窗类"""

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content=content, parent=parent)
        self.lineEdit = LineEdit(self)
        tips = "Please enter 3 to 20 characters consisting of '0-9','a-z','A-Z','_'"
        self.tipsLabel = CaptionLabel(tips, self)
        self.tipsLabel.setTextColor("#606060", "#d2d2d2")
        self.tipsLabel.setObjectName("contentLabel")
        self.tipsLabel.setWordWrap(True)
        self.tipsLabel.setFixedSize(250, 40)
        self.lineEdit.setFixedSize(250, 33)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.move(45, 70)
        self.tipsLabel.move(47, 110)
        self.setTitleBarVisible(False)


class StartPanel(QtWidgets.QWidget):
    """主页开始面板"""

    workSpaceChanged = pyqtSignal(object)

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

    def _on_current_item_click(self, item: typing.Optional[QtWidgets.QListWidgetItem]):
        """
        点击按钮触发不同的事件
        :param: item: 所点击的条目
        """
        if item.text() == "New Workspace":
            self._new_workspace()
        if item.text() == "Open Workspace":
            self._open_workspace()

    def _new_workspace(self):
        """新建一个工作空间"""
        workspace_name = self.showDialog()
        if workspace_name:
            dname = QtWidgets.QFileDialog.getExistingDirectory(self, "New Workspace")
            if dname:
                path = os.path.join(dname, f"{workspace_name}.lmdb")
                if os.path.exists(path):
                    show_error("Exist old workspace!", self.window())
                    return
                url = "http://10.11.140.13:8000/f/d5ffeb40db12404e8fb5/?dl=1"
                downobj = DownLoadFile(url, path)
                downobj.download_from_url()
                sync_recent_config(
                    workspace_name, f"{dname}/{workspace_name}.lmdb", self._worker_count
                )
                self.workSpaceChanged.emit(Workspace(path, self._worker_count))
            self.listWidget.clearSelection()

    def showDialog(self):
        """配置弹窗并显示，用户输入符合标准的名称后将其返回"""
        title = "Please name your workspace:"
        content = "\n| \n| \n| \n| \n|"
        w = InputDialog(title, content, self)
        if w.exec():
            str = w.lineEdit.text()
            res = re.search("^\w{3,20}$", str)
            if not res:
                show_error("Invalid name! ", self.window())
            else:
                return str
        else:
            return False

    def _open_workspace(self):
        """打开一个工作空间"""
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Workspace", filter="Workspace files (*.lmdb)"
        )
        workspace_name = fname.split("/")[len(fname.split("/")) - 1].replace(
            ".lmdb", ""
        )
        if fname:
            get_worker_count = sync_recent_config(workspace_name, fname)
            self.workSpaceChanged.emit(Workspace(fname, get_worker_count))
        self.listWidget.clearSelection()

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

    workSpaceChanged = pyqtSignal(object)

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

    def _on_current_item_click(self, item: typing.Optional[RecentWorkspaceItem]):
        """点击一个 最近打开 的条目"""
        fpath = item.getWorkspacePath()
        fname = item.getWorkspaceName()
        if os.path.exists(fpath):
            get_worker_count = sync_recent_config(fname, fpath)
            self.workSpaceChanged.emit(Workspace(fpath, get_worker_count))
        else:
            # 未找到文件
            sync_recent_config(fname, fpath, state="del")
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
        self.bottom_left_panel_layout.workSpaceChanged.connect(
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
