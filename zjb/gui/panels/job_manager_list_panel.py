# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem
from qfluentwidgets import (
    FluentIcon,
    FluentWindow,
    ListWidget,
    ScrollArea,
    SubtitleLabel,
)

from .._global import GLOBAL_SIGNAL
from ..pages.job_list_page import JobListPage
from ..pages.worker_manager_page import WorkerManagerPage


class JobManagerInterface(ScrollArea):
    """JobManagerInterface 目录列表"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.listWidget = ListWidget(self)

        jobItem = QListWidgetItem("Job List")
        jobItem.setIcon(FluentIcon.DOCUMENT.icon())
        self.listWidget.addItem(jobItem)

        workerItem = QListWidgetItem("Worker Manager")
        workerItem.setIcon(FluentIcon.DEVELOPER_TOOLS.icon())
        self.listWidget.addItem(workerItem)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.listWidget)

        self.setObjectName("JobManagerInterface")
        self.setStyleSheet("#JobManagerInterface{background:transparent;border:none}")

        self.listWidget.itemClicked.connect(self._itemClicked)

    def _itemClicked(self, item: QListWidgetItem):
        if item.text() == "Job List":
            GLOBAL_SIGNAL.requestAddPage.emit(
                JobListPage("Job List", "Job List", FluentIcon.DOCUMENT)
            )

        if item.text() == "Worker Manager":
            GLOBAL_SIGNAL.requestAddPage.emit(
                WorkerManagerPage(
                    "Worker Manager", "Worker Manager", FluentIcon.DEVELOPER_TOOLS
                )
            )
