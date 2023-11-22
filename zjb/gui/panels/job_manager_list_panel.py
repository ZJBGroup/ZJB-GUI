# coding:utf-8
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem
from qfluentwidgets import FluentIcon, ListWidget, ScrollArea
from qfluentwidgets.common.icon import FluentIconEngine, Icon

from .._global import GLOBAL_SIGNAL
from ..pages.base_page import BasePage
from ..pages.job_list_page import JobListPage
from ..pages.worker_manager_page import WorkerManagerPage


class JobManagerInterface(ScrollArea):
    """JobManagerInterface 目录列表"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.listWidget = ListWidget(self)

        jobItem = QListWidgetItem("Job List")
        jobItem.setIcon(QIcon(FluentIconEngine(Icon(FluentIcon.DOCUMENT))))
        self.listWidget.addItem(jobItem)

        workerItem = QListWidgetItem("Worker Manager")
        workerItem.setIcon(QIcon(FluentIconEngine(Icon(FluentIcon.DEVELOPER_TOOLS))))
        self.listWidget.addItem(workerItem)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.listWidget)

        self.setObjectName("JobManagerInterface")
        self.setStyleSheet("#JobManagerInterface{background:transparent;border:none}")

        self.listWidget.itemClicked.connect(self._itemClicked)

    def _itemClicked(self, item: QListWidgetItem):
        """列表条目的点击"""
        GLOBAL_SIGNAL.requestAddPage.emit(item.text(), self._addpage)

    def _addpage(self, routeKey: str) -> BasePage:
        """层叠窗口区域新增加一个页面

        Parameters:
        ----------
        routeKey: str
            需要创建的页面的 RouteKey, 表示该页面的唯一标识

        Returns:
        ----------
        BasePage:
            返回创建的页面
        """
        if routeKey == "Job List":
            _page = JobListPage(routeKey, "Job List", FluentIcon.DOCUMENT)
            _page.setWorkspace()
            return _page

        if routeKey == "Worker Manager":
            _page = WorkerManagerPage(
                routeKey, "Worker Manager", FluentIcon.DEVELOPER_TOOLS
            )
            _page.work_panel.setWorkspace()
            return _page
