import os
import typing
from enum import IntEnum
from threading import Thread
from time import sleep

import psutil
from PyQt5 import QtWidgets
from PyQt5.QtCore import QEasingCurve, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    FlowLayout,
    FluentIcon,
    IconWidget,
    IndeterminateProgressRing,
    InfoBadge,
    PrimaryPushButton,
    SmoothScrollArea,
    SpinBox,
    SubtitleLabel,
)
from zjb.doj.worker import Worker
from zjb.main.manager.workspace import Workspace

from .._global import GLOBAL_SIGNAL
from ..common.utils import show_error
from .base_page import BasePage


class ProcessWorker:
    ...


class CardSize(IntEnum):
    """卡片的尺寸"""

    WIDTH = 260
    HEIGHT = 150


class WorkerCard(CardWidget):
    """用来表示一个 Worker 的卡片"""

    _workerStateChangedSignal = pyqtSignal(ProcessWorker)  # Worker 状态发生变化时候的信号

    def __init__(self, item: Worker, index, parent=None):
        super().__init__(parent)
        self.setFixedHeight(CardSize.HEIGHT)
        self.setFixedWidth(CardSize.WIDTH)
        # 绑定对应Worker的数据
        self._worker = item
        self._state = "waiting" if item.is_idel() else "working"
        self._content = f"State：\t\t{self._state}"
        # 标题
        self.titleLabel = BodyLabel(f"{index}-Worker", self)
        self.titleLabel.setObjectName("WorkerTitle")
        # 状态信息
        self.stateLabel = CaptionLabel(self._content, self)
        self.stateLabel.setTextColor("#606060", "#d2d2d2")
        self.stateLabel.setWordWrap(True)
        self.stateLabel.setFixedHeight(18)
        self.stateLabel.setAlignment(Qt.AlignTop)
        # cpu 信息
        self.cpuLabel = CaptionLabel("Memory：\t0% \nCPU：\t\t0%", self)
        self.cpuLabel.setTextColor("#606060", "#d2d2d2")
        self.cpuLabel.setWordWrap(True)
        self.cpuLabel.setFixedHeight(33)
        self.cpuLabel.setAlignment(Qt.AlignTop)
        self.psutil_process = psutil.Process(self._worker.process.pid)
        # 运行中的 Job 信息
        self.jobLabel = CaptionLabel("Job：\t\tNone", self)
        self.jobLabel.setTextColor("#606060", "#d2d2d2")
        self.jobLabel.setWordWrap(True)
        self.jobLabel.setFixedHeight(40)
        self.jobLabel.setAlignment(Qt.AlignTop)
        # 第一行布局
        self.button_Layout = QHBoxLayout()
        self.button_Layout.addWidget(self.titleLabel, 0, Qt.AlignLeft)
        # 进度环
        self.progressRing = IndeterminateProgressRing(self)
        self.progressRing.setFixedSize(25, 25)
        self.button_Layout.addWidget(self.progressRing, 0, Qt.AlignRight)
        # 文字内容布局
        self.content_Layout = QVBoxLayout()
        self.content_Layout.setSpacing(0)
        self.content_Layout.setContentsMargins(0, 0, 0, 0)
        self.content_Layout.addWidget(self.stateLabel, 0, Qt.AlignTop)
        self.content_Layout.addWidget(self.cpuLabel, 0, Qt.AlignTop)
        self.content_Layout.addWidget(self.jobLabel, 0, Qt.AlignTop)
        self.content_Layout.setAlignment(Qt.AlignTop)
        # 整体布局
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(20, 11, 11, 11)
        self.outer_layout.addLayout(self.button_Layout)
        self.outer_layout.addLayout(self.content_Layout)
        self._setIdle()

        # 监测状态的变化 当 'state' 发生变化的时候，调用 self._stateChanged
        # self._worker.observe(self._stateChanged, "state", dispatch="same")
        # TODO: 监测 worker 状态

    def _setWorking(self):
        """将UI样式设置为工作中的状态"""
        self.progressRing.setVisible(True)
        self.setStyleSheet("#WorkerTitle{color:red;font-size:20pt}")

    def _setIdle(self):
        """将UI样式设置为空闲的状态"""
        self.progressRing.setVisible(False)
        self.setStyleSheet("#WorkerTitle{color:green;font-size:20pt}")

    def _stateChanged(self, _):
        """更新卡片的内容"""
        if str(self._worker.state.name) == "WORKING":
            self._setWorking()
            self.jobLabel.setText(f"Job：\n{self._worker._job.gid}")
        else:
            self._setIdle()
            self.jobLabel.setText("Job：\t\tNone")
        self._content = f"State：\t\t{self._worker.state.name.lower() }"
        self.stateLabel.setText(self._content)
        self._workerStateChangedSignal.emit(self._worker)

    def setCpuInfo(self, info):
        """
        修改卡片中的 CPU 信息
        :param: info: 新的CPU信息
        """
        self.cpuLabel.setText(info)

    def setTitle(self, index):
        """
        修改卡片中的 Title 信息
        :param: index: 当前卡片的索引
        """
        self.titleLabel.setText(f"{index}-Worker")

    def getWorker(self):
        """获取当前的 Worker"""
        return self._worker

    def getPsutilProcess(self):
        """获取当前的 psutil_process 实例"""
        return self.psutil_process


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

        # 工具栏布局
        self.toolsBar = QHBoxLayout()
        self.toolsBar.setAlignment(Qt.AlignLeft)
        self.toolsBar.setSpacing(10)

        # 自定义增减板块
        self.spinBox = SpinBox()
        self.spinBox.setMaximum(self.max_card_num)
        self.spinBox.setDisabled(True)
        self.spinBox.editingFinished.connect(self._spinBoxChanged)
        self.spinBox.upButton.clicked.connect(self._upButtonClicked)
        self.spinBox.downButton.clicked.connect(self._downButtonClicked)

        # 按钮
        self.primaryToolButton = PrimaryPushButton(
            "Delete Idle", self, FluentIcon.DELETE
        )
        self.primaryToolButton.clicked.connect(self._deleteIdelProcess)

        # 允许的最大数目的 badge
        self.max_badge = InfoBadge.attension(f"Max:{self.max_card_num}")
        self.max_badge.setFont(QFont("", 14, QFont.Weight.Normal))
        # 总数的 badge
        self.all_badge = InfoBadge.custom("All:0", "#005fb8", "#60cdff")
        self.all_badge.setFont(QFont("", 14, QFont.Weight.Normal))
        # 忙碌的 badge
        self.busy_badge = InfoBadge.error("Busy:0")
        self.busy_badge.setFont(QFont("", 14, QFont.Weight.Normal))
        # 空闲的 badge
        self.idel_badge = InfoBadge.success("Idel:0")
        self.idel_badge.setFont(QFont("", 14, QFont.Weight.Normal))

        # 工具栏布局
        self.toolsBar.addWidget(self.spinBox)
        self.toolsBar.addWidget(self.primaryToolButton)
        self.toolsBar.addStretch()
        self.toolsBar.addWidget(self.max_badge)
        self.toolsBar.addWidget(self.all_badge)
        self.toolsBar.addWidget(self.busy_badge)
        self.toolsBar.addWidget(self.idel_badge)

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
        self.main_layout.addLayout(self.toolsBar)
        self.main_layout.addWidget(self.card_layout_container)
        self.main_layout.setAlignment(Qt.AlignTop)

        # 线程更新每个卡片中的CPU信息
        def updateCPUInfo():
            while True:
                sleep(1)
                for i in range(self.card_layout.count()):
                    item = self.card_layout.itemAt(i)
                    pInformation = item.widget().getPsutilProcess()
                    pText = f"Memory：\t{ round(pInformation.memory_percent(),4) }%"
                    cpuText = f"CPU：\t\t{ round(pInformation.cpu_percent(),4)}%"
                    item.widget().setCpuInfo(f"{pText}\n{cpuText}")

        self.cpuThread = Thread(target=updateCPUInfo, daemon=True)
        self.cpuThread.start()

        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(self.setWorkspace)

    def setWorkspace(self, workspace: Workspace):
        """
        设置工作空间，同步相应的数据
        :param: workspace: 一个工作空间
        """
        self._workspace = workspace
        print("worker setWorkspace", workspace)

        if not self._workspace == None:
            self._workspace.observe(print, "workers.items", dispatch="same")
            self.spinBox.setDisabled(False)
            # 保证在首页切换工作空间的时候 清除列表中之前的卡片
            self.card_layout.takeAllWidgets()
            initWorkers = self._workspace.workers
            for item in initWorkers:
                self._addCard(item)
            self.card_layout.setGeometry(self.card_layout.geometry())  # 处理元素堆叠问题
            self.other_workers = self._workspace.workers
            self.busy_workers = []
            self._updateToolsBar(
                count=len(self._workspace.workers),
                idel_num=len(self.other_workers),
                all_num=len(self._workspace.workers),
            )

    def _deleteIdelProcess(self):
        """清除所有空闲的进程"""
        delItem = []
        for item in self.other_workers:
            delItem.append(item)
        for item in delItem:
            self._deleteProcessWorker(item)
        self._updateToolsBar(
            count=len(self.busy_workers),
            idel_num=len(self.other_workers),
            all_num=len(self.busy_workers),
        )

    def _spinBoxChanged(self):
        """spinBox 手动输入完成以后"""
        _all_num = len(self.busy_workers) + len(self.other_workers)
        if int(self.spinBox.text()) > _all_num:
            # 此时需要增加更多的 card
            for _ in range(int(self.spinBox.text()) - _all_num):
                self._upButtonClicked()
            self._updateToolsBar(all_num=int(self.spinBox.text()))
        elif int(self.spinBox.text()) < _all_num:
            # 此时需要删除多余的 card
            diff = _all_num - int(self.spinBox.text())
            busy_num = len(self.busy_workers)
            if int(self.spinBox.text()) < busy_num:
                # 设置的数量 超过正在运行的进程数
                show_error(
                    f"Over {self.spinBox.text()} Processes are WORKING", self.window()
                )
            else:
                delItem = []
                # 先找到要删除的项
                for item in self.other_workers:
                    if diff == 0:
                        break
                    self._deleteProcessWorker(item)
                    delItem.append(item)
                    diff = diff - 1
                # 逐个在 self.other_workers 中删除
                for item in delItem:
                    if item in self.other_workers:
                        self.other_workers.remove(item)
                self._updateToolsBar(idel_num=len(self.other_workers))

    def _updateToolsBar(self, count=None, all_num=None, busy_num=None, idel_num=None):
        """
        更新工具栏中的各项数据
        :param: count: spinBox中的可编辑的数据
        :param: all_num: badge中的总数
        :param: busy_num: badge中运行中的进程数
        :param: idel_num: badge中的空闲进程数
        """
        if not count == None:
            self.spinBox.setValue(count)
        if not all_num == None:
            self.all_badge.setText(f"All:{all_num}")
        if not busy_num == None:
            self.busy_badge.setText(f"Busy:{busy_num}")
        if not idel_num == None:
            self.idel_badge.setText(f"Idel:{idel_num}")

    def _upButtonClicked(self):
        """点击 spinBox 的向上按钮"""
        if not self._workspace:
            show_error("Please 'Open' or 'New' a workspace first", self.window())
        else:
            if int(self.card_layout.count()) == self.max_card_num:
                show_error("Unable to add more processes", self.window())
            else:
                self._workspace.start_workers(1)
                return
                newWorker = ProcessWorker(manager=self._workspace.jm)
                newWorker.start()
                self._workspace.jm.workers.append(newWorker)
                self._addCard(newWorker)
                self.workerCountChanged.emit(
                    len(self.busy_workers) + len(self.other_workers)
                )
                self._updateToolsBar(
                    all_num=len(self.busy_workers) + len(self.other_workers)
                )

    def _downButtonClicked(self):
        """点击 spinBox 的向下按钮"""
        if len(self.other_workers) == 0:
            show_error("No Idel Process can be deleted", self.window())
            self._updateToolsBar(count=len(self.busy_workers))
        else:
            return
            delworker = self.other_workers[len(self.other_workers) - 1]
            self._deleteProcessWorker(delworker)
            if delworker in self.other_workers:
                self.other_workers.remove(delworker)
            self._updateToolsBar(
                all_num=len(self.busy_workers) + len(self.other_workers),
                idel_num=len(self.other_workers),
            )

    def _addCard(self, item: Worker):
        """
        在界面上添加一个表示Worker的卡片
        :param: item: 一个Worker的进程
        """
        card = WorkerCard(item, self.card_layout.count() + 1)
        self.card_layout.addWidget(card)
        card._workerStateChangedSignal.connect(self._stateChanged)

    def _deleteProcessWorker(self, worker: ProcessWorker):
        """
        删除一个表示Worker的卡片
        :param: worker: 一个Worker的信息
        """
        # worker.terminate()
        return
        tempItem = worker
        self._workspace.jm.workers.remove(worker)
        self.workerCountChanged.emit(len(self.busy_workers) + len(self.other_workers))
        for i in range(self.card_layout.count()):
            item = self.card_layout.itemAt(i)
            if item and item.widget().getWorker() == worker:
                self.card_layout.takeAt(i)
                item.widget().deleteLater()
                break
        self._updateIndex()

        def terminateProcess():
            # 单独开一个线程用来关闭不要的进程
            tempItem.terminate()

        self.deleteThread = Thread(
            target=terminateProcess,
            daemon=True,
        )
        self.deleteThread.start()

    def _stateChanged(self, worker: Worker):
        """
        每一个 worker 发生变化的时候，更新工具栏相应的数据
        :param: worker: 一个Worker的信息
        """
        if not worker.is_idel():
            # 忙碌
            if not worker in self.busy_workers:
                self.busy_workers.append(worker)
            if worker in self.other_workers:
                self.other_workers.remove(worker)
        elif worker.is_idel():
            # 空闲
            if worker in self.busy_workers:
                self.busy_workers.remove(worker)
            if not worker in self.other_workers:
                self.other_workers.append(worker)
        self._updateToolsBar(
            busy_num=len(self.busy_workers), idel_num=len(self.other_workers)
        )

    def _updateIndex(self):
        # 更新卡片的 索引
        for i in range(self.card_layout.count()):
            item = self.card_layout.itemAt(i)
            item.widget().setTitle(i + 1)


class WorkerManagerPage(BasePage):
    """Tab interface"""

    def __init__(self, routeKey: str, title: str, icon, parent=None):
        super().__init__(routeKey, title, icon, parent)
        self.work_panel = WorkerPanel("work_panel")
        self.vBoxLayout = QtWidgets.QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.work_panel)
        self.setObjectName(routeKey)
