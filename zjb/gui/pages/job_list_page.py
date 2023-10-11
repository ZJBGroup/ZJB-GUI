import typing

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QStackedWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from qfluentwidgets import Dialog, Pivot, TableWidget

from .base_page import BasePage

# from zjb.base.job import Job
# from zjb.main.workspace import Workspace


class InputDialog(Dialog):
    """显示表格条目详细信息的弹窗"""

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content=content, parent=parent)
        self.contentLabel.setWordWrap(True)
        self.setTitleBarVisible(False)
        self.cancelButton.hide()
        self.yesButton.setText("Close")


class JobTable(TableWidget):
    """一个表格类"""

    def __init__(self, parent=None, num=0, header=[]):
        super().__init__(parent)
        self.setWordWrap(False)
        self.verticalHeader().hide()
        self.setColumnCount(num)
        self.setHorizontalHeaderLabels(header)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setMinimumSectionSize(100)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.setSelectionMode(QAbstractItemView.NoSelection)


class JobListPage(BasePage):
    """作业列表页面"""

    def __init__(self, routeKey: str, title: str, icon, parent=None):
        super().__init__(routeKey, title, icon, parent)
        self.setObjectName(routeKey)
        self._workspace = None

        # 配置垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(5, 0, 5, 5)
        self.vBoxLayout.setObjectName("verticalLayout")

        # 配置导航
        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignHCenter)
        self.vBoxLayout.addWidget(self.stackedWidget)

        # 配置全部工作的列表
        self.all_job_header = ["GID", "State", "Function Type", "Error"]
        self.other_job_header = ["GID", "State", "Function Type"]
        self.all_job_table = JobTable(self.stackedWidget, 4, self.all_job_header)
        self.finished_job_table = JobTable(self.stackedWidget, 3, self.other_job_header)
        self.running_job_table = JobTable(self.stackedWidget, 3, self.other_job_header)
        self.failed_job_table = JobTable(self.stackedWidget, 4, self.all_job_header)
        # 表单禁用编辑功能
        self.all_job_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.finished_job_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.running_job_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.failed_job_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 初始化导航
        self.addSubInterface(self.all_job_table, "all_job", "all")
        self.addSubInterface(self.running_job_table, "running_job", "running")
        self.addSubInterface(self.finished_job_table, "finished_job", "finished")
        self.addSubInterface(self.failed_job_table, "failed_job", "failed")
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.pivot.setCurrentItem(self.all_job_table.objectName())
        self.stackedWidget.setCurrentWidget(self.all_job_table)

        # 各个 table 绑定条目的点击事件
        self.all_job_table.itemClicked.connect(self.showDialog)
        self.finished_job_table.itemClicked.connect(self.showDialog)
        self.running_job_table.itemClicked.connect(self.showDialog)
        self.failed_job_table.itemClicked.connect(self.showDialog)

    def addSubInterface(self, widget: typing.Optional[JobTable], objectName, text):
        """
        增加导航，并与对应的 Table 绑定
        :param: widget: 导航项对应要展示的控件
        :param: objectName: 控件的命名，作为 Key
        :param: text: 导航的名称，显示在导航上
        """
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
        )

    def showDialog(self, item: QTableWidgetItem):
        """
        配置弹窗并显示点击条目的具体信息
        :param: item: 点击的表单条目
        """
        state = item.tableWidget().item(item.row(), 1).text()
        type = item.tableWidget().item(item.row(), 2).text()
        error = (
            item.tableWidget().item(item.row(), 3).text()
            if item.tableWidget().item(item.row(), 3)
            else "-"
        )

        title = item.tableWidget().item(item.row(), 0).text()
        content = f"State:\t{state} \nType:\t{type} \nError:\t{error}"
        w = InputDialog(title, content, self)
        w.exec()

    def onCurrentIndexChanged(self, index):
        """
        点击导航条目绑定的槽函数
        :param: index: 控件索引
        """
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())

    # def setWorkspace(self, workspace: typing.Optional[Workspace]):
    #     """
    #     设置并同步工作空间数据
    #     :param: workspace: 工作空间数据
    #     """
    #     self._workspace = workspace
    #     self._sync_table()
    #     self._sync_layout(self.all_job_table)
    #     self._sync_layout(self.running_job_table)
    #     self._sync_layout(self.finished_job_table)
    #     self._sync_layout(self.failed_job_table)

    def _sync_layout(self, widget: typing.Optional[JobTable]):
        """
        根据内容同步调整 table 的布局
        :param: widget: 控件，主要是table表格
        """
        widget.resizeColumnsToContents()
        widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        widget.horizontalHeader().setMinimumSectionSize(100)
        widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)

    def _sync_table(self):
        """拿到工作空间数据以后，往表格中加数据，往导航按钮上加总数"""
        self.all_job_table.clearContents()
        self.running_job_table.clearContents()
        self.finished_job_table.clearContents()
        self.failed_job_table.clearContents()
        self.pivot.removeWidget("all_job")
        self.pivot.removeWidget("finished_job")
        self.pivot.removeWidget("running_job")
        self.pivot.removeWidget("failed_job")
        self._all_job = []
        self._finished_job = []
        self._running_job = []
        self._failed_job = []

        # 将所有的数据拆分到不用的表中
        # for item in self._workspace.dm.find_by_type(Job):
        #     _item = [
        #         str(item),
        #         str(item.state.name),
        #         item.func_type.__name__,
        #         str(item.error) if item.error != None else "-",
        #     ]
        #     self._all_job.append(_item)
        #     if str(item.state.name) == "WAIT_WORKER":
        #         self._running_job.append(_item)
        #     if str(item.state.name) == "DONE":
        #         self._finished_job.append(_item)
        #     if str(item.state.name) == "ERROR":
        #         self._failed_job.append(_item)

        # 设置每个 table 的行数
        self.all_job_table.setRowCount(len(self._all_job))
        self.running_job_table.setRowCount(len(self._running_job))
        self.finished_job_table.setRowCount(len(self._finished_job))
        self.failed_job_table.setRowCount(len(self._failed_job))

        # 将各个列表的总数加到导航上
        self.addSubInterface(
            self.all_job_table, "all_job", f"all({len(self._all_job)})"
        )
        self.addSubInterface(
            self.running_job_table, "running_job", f"running({len(self._running_job)})"
        )
        self.addSubInterface(
            self.finished_job_table,
            "finished_job",
            f"finished({len(self._finished_job)})",
        )
        self.addSubInterface(
            self.failed_job_table, "failed_job", f"failed({len(self._failed_job)})"
        )
        self.pivot.setCurrentItem(self.all_job_table.objectName())

        # 往各个 table 中添加数据，并做样式设置
        # i 表示行 j 表示列
        for i, jobInfo in enumerate(self._all_job):
            for j in range(4):
                self.all_job_table.setItem(i, j, QTableWidgetItem(jobInfo[j]))
                self.all_job_table.item(i, j).setTextAlignment(Qt.AlignCenter)
                if jobInfo[1] == "ERROR":
                    self.all_job_table.item(i, j).setForeground(
                        QBrush(QColor(255, 0, 0))
                    )
        for i, jobInfo in enumerate(self._running_job):
            for j in range(3):
                self.running_job_table.setItem(i, j, QTableWidgetItem(jobInfo[j]))
                self.running_job_table.item(i, j).setTextAlignment(Qt.AlignCenter)
        for i, jobInfo in enumerate(self._finished_job):
            for j in range(3):
                self.finished_job_table.setItem(i, j, QTableWidgetItem(jobInfo[j]))
                self.finished_job_table.item(i, j).setTextAlignment(Qt.AlignCenter)
        for i, jobInfo in enumerate(self._failed_job):
            for j in range(4):
                self.failed_job_table.setItem(i, j, QTableWidgetItem(jobInfo[j]))
                self.failed_job_table.item(i, j).setTextAlignment(Qt.AlignCenter)
                self.failed_job_table.item(i, j).setForeground(
                    QBrush(QColor(255, 0, 0))
                )
