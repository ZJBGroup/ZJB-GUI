import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import QEasingCurve, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import FlowLayout, SmoothScrollArea
from zjb.doj.worker import Worker
from zjb.main.manager.workspace import Workspace

from .._global import GLOBAL_SIGNAL, get_workspace, get_workspace_path
from ..common.config_path import sync_recent_config
from ..common.utils import show_error
from ..widgets.worker_card import WorkerCard
from ..widgets.worker_tools_bar import WorkerToolsBar
from .base_page import BasePage


class WorkerPanel(SmoothScrollArea):
    """陈列Worker卡片的面板"""

    workerCountChanged = pyqtSignal(int)  # worker_count 发生变化时的信号

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName(text.replace(" ", "_"))
        self._workspace = None
        self.max_card_num = os.cpu_count()
        self.busy_workers = []  # 存放忙碌中的 worker
        self.other_workers = []  # 存放非忙碌的 worker

        # 工具栏
        self.toolsBar = WorkerToolsBar(self.max_card_num)
        self.toolsBar.spinBox.editingFinished.connect(self._spinBoxChanged)
        self.toolsBar.spinBox.upButton.clicked.connect(self._upButtonClicked)
        self.toolsBar.spinBox.downButton.clicked.connect(self._downButtonClicked)
        self.toolsBar.primaryToolButton.clicked.connect(self._deleteIdleProcess)

        # workerCard 布局
        self.card_layout = FlowLayout(needAni=True)
        self.card_layout.setAnimation(250, QEasingCurve.OutQuad)
        self.card_layout.setContentsMargins(0, 10, 0, 0)
        self.card_layout.setVerticalSpacing(10)
        self.card_layout.setHorizontalSpacing(10)

        # 滚动布局相关
        self.card_layout_container = QWidget()
        self.card_layout_container.setLayout(self.card_layout)
        self.container = QWidget(self)
        self.setStyleSheet("QWidget{background-color: transparent;border:none;}")
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.addWidget(self.toolsBar)
        self.main_layout.addWidget(self.card_layout_container)
        self.main_layout.setAlignment(Qt.AlignTop)

        self.watch_cpu_info = QTimer(self)
        self.watch_cpu_info.start(1000)
        self.watch_cpu_info.timeout.connect(self.updateCPUInfo)

        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(self.setWorkspace)

    def updateCPUInfo(self):
        """更新每个卡片中的CPU信息"""
        for i in range(self.card_layout.count()):
            item = self.card_layout.itemAt(i)
            if not item.widget() == None:
                pInformation = item.widget().getPsutilProcess()
                _memory = round(pInformation.memory_percent(), 4)
                _cpu = round(pInformation.cpu_percent(), 4)
                item.widget().setCpuInfo(_memory, _cpu)
                if item.widget().getWorker().is_idle():
                    item.widget()._setIdle()
                    if not item.widget().getWorker() in self.other_workers:
                        self.other_workers.append(item.widget().getWorker())
                        self.busy_workers.remove(item.widget().getWorker())
                else:
                    item.widget()._setWorking()
                    if not item.widget().getWorker() in self.busy_workers:
                        self.busy_workers.append(item.widget().getWorker())
                        self.other_workers.remove(item.widget().getWorker())
                self._updateToolsBar(
                    idle_num=len(self.other_workers), busy_num=len(self.busy_workers)
                )

    def setWorkspace(self):
        """
        设置工作空间，同步相应的数据
        :param: workspace: 一个工作空间
        """
        self._workspace = get_workspace()
        if not self._workspace == None:
            # 监听 workers 数量的变化
            self._workspace.observe(
                self._workersNumChanged, "workers.items", dispatch="same"
            )
            self.toolsBar.setSpinBoxDisabled(False)
            # 保证在首页切换工作空间的时候 清除列表中之前的卡片
            self.card_layout.takeAllWidgets()
            init_workers = self._workspace.workers
            self.other_workers = []
            self.busy_workers = []
            for item in init_workers:
                self.other_workers.append(item)
                self._addCard(item)
            self.card_layout.setGeometry(self.card_layout.geometry())  # 处理元素堆叠问题

            self._updateToolsBar(
                count=len(self._workspace.workers),
                idle_num=len(self.other_workers),
                all_num=len(self._workspace.workers),
            )

    def _workersNumChanged(self, detail):
        """监听 Worker 数量发生变化时候的回调函数

        Parameters:
        ----------
        detail: str
            变化的具体内容
        """
        [_object, _index, _removed, _added] = [
            detail.object,
            detail.index,
            detail.removed,
            detail.added,
        ]
        if not _added == []:
            for item in _added:
                self._addCard(item)
                self.other_workers.append(item)

        if not _removed == []:
            for item in _removed:
                self._deleteCard(item)
                self.other_workers.remove(item)
        self._updateToolsBar(
            count=len(_object), idle_num=len(self.other_workers), all_num=len(_object)
        )
        self.card_layout.setGeometry(self.card_layout.geometry())
        self._configWorkerCount(_index + 1)

    def _configWorkerCount(self, worker_count):
        """
        新增、删除 Worker 的时候 更新本地配置文件
        :param: worker_count: worker数目
        """
        path = get_workspace_path()
        name = path.split("/")[len(path.split("/")) - 1]
        sync_recent_config(name, path, worker_count)

    def _addCard(self, item: Worker):
        """
        在界面上添加一个表示Worker的卡片
        :param: item: 一个Worker的进程
        """
        card = WorkerCard(item, self.card_layout.count() + 1)
        self.card_layout.addWidget(card)

    def _deleteCard(self, worker: Worker):
        """
        从界面上删除一个表示Worker的卡片
        :param: worker: 一个Worker的信息
        """
        for i in range(self.card_layout.count()):
            item = self.card_layout.itemAt(i)
            if item.widget() and item.widget().getWorker() == worker:
                self.card_layout.takeAt(i)
                item.widget().deleteLater()
                break
        self._updateIndex()

    def _upButtonClicked(self):
        """点击 spinBox 的向上按钮"""
        if not self._workspace:
            show_error("Please 'Open' or 'New' a workspace first", self.window())
        else:
            if int(self.card_layout.count()) == self.max_card_num:
                show_error("Unable to add more processes", self.window())
            else:
                self._workspace.start_workers(1)

    def _downButtonClicked(self):
        """点击 spinBox 的向下按钮"""
        if len(self.other_workers) == 0:
            show_error("No Idle Process can be deleted", self.window())
        else:
            self._workspace.remove_idle_workers(1)

    def _deleteIdleProcess(self):
        """清除所有空闲的进程"""
        if self._workspace:
            self._workspace.remove_idle_workers()

    def _updateToolsBar(self, count=None, all_num=None, busy_num=None, idle_num=None):
        """
        更新工具栏中的各项数据
        :param: count: spinBox中的可编辑的数据
        :param: all_num: badge中的总数
        :param: busy_num: badge中运行中的进程数
        :param: idle_num: badge中的空闲进程数
        """
        self.toolsBar.updateToolsBar(count, all_num, busy_num, idle_num)

    def _updateIndex(self):
        # 更新卡片的 索引
        for i in range(self.card_layout.count()):
            item = self.card_layout.itemAt(i)
            item.widget().setTitle(i + 1)

    def _spinBoxChanged(self):
        """spinBox 手动输入完成以后"""
        _all_num = len(self.busy_workers) + len(self.other_workers)
        input_num = self.toolsBar.getSpinBoxNum()
        if input_num > _all_num:
            # 此时需要增加更多的 card
            self._workspace.start_workers(input_num - _all_num)
        elif input_num < _all_num:
            # 此时需要删除多余的 card
            diff = _all_num - input_num
            busy_num = len(self.busy_workers)
            if input_num < busy_num:
                # 设置的数量 超过正在运行的进程数
                show_error(
                    f"Over {input_num} Processes are WORKING",
                    self.window(),
                )
            else:
                self._workspace.remove_idle_workers(diff)


class WorkerManagerPage(BasePage):
    """Tab interface"""

    def __init__(self, routeKey: str, title: str, icon, parent=None):
        super().__init__(routeKey, title, icon, parent)
        self.work_panel = WorkerPanel("work_panel")
        self.vBoxLayout = QtWidgets.QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.work_panel)
        self.setObjectName(routeKey)
