from enum import IntEnum

import psutil
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    IndeterminateProgressRing,
)
from zjb.doj.worker import Worker


class CardSize(IntEnum):
    """卡片的尺寸"""

    WIDTH = 260
    HEIGHT = 150


class WorkerCard(CardWidget):
    """用来表示一个 Worker 的卡片"""

    def __init__(self, item: Worker, index, parent=None):
        super().__init__(parent)
        self.setFixedHeight(CardSize.HEIGHT)
        self.setFixedWidth(CardSize.WIDTH)
        # 绑定对应Worker的数据
        self._worker = item
        self._state = "waiting" if item.is_idle() else "working"
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
        if item.is_idle():
            self._setIdle()
        else:
            self._setWorking()

    def _setWorking(self):
        """将UI样式设置为工作中的状态"""
        self.setState("working")
        self.progressRing.setVisible(True)
        self.setStyleSheet("#WorkerTitle{color:red;font-size:20pt}")

    def _setIdle(self):
        """将UI样式设置为空闲的状态"""
        self.setState("waiting")
        self.progressRing.setVisible(False)
        self.setStyleSheet("#WorkerTitle{color:green;font-size:20pt}")

    def setState(self, state):
        """
        修改卡片中的 Worker 状态
        :param: state: 状态信息
        """
        self.stateLabel.setText(state)

    def setCpuInfo(self, memory, cpu):
        """
        修改卡片中的 CPU 信息
        :param: memory: 内存占用
        :param: cpu: cpu利用率
        """
        self.cpuLabel.setText(f"Memory：\t{memory}% \nCPU：\t\t{cpu}%")

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
