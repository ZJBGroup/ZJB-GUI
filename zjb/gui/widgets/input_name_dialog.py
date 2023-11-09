import re

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget
from qfluentwidgets import (
    CaptionLabel,
    ComboBox,
    LineEdit,
    MessageBoxBase,
    SubtitleLabel,
)
from zjb.dos.data import Data
from zjb.main.api import Project, SpaceCorrelation, Subject

from .._global import get_workspace


class WorkspaceInputDialog(MessageBoxBase):
    """输入工作空间名称的弹窗类"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.flag = ""
        self.titleLabel = SubtitleLabel(title)
        self.titleLabel.setContentsMargins(0, 0, 0, 10)
        self.viewLayout.addWidget(self.titleLabel)

        self.lineEdit = LineEdit(self)
        self.lineEdit.setFixedSize(250, 33)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.move(45, 70)

        tips = "Please enter 1 to 20 characters consisting of '0-9','a-z','A-Z','_'"
        self.tipsLabel = CaptionLabel(tips, self)
        self.tipsLabel.setTextColor("#606060", "#d2d2d2")
        self.tipsLabel.setObjectName("contentLabel")
        self.tipsLabel.setWordWrap(True)
        self.tipsLabel.setFixedSize(250, 40)
        self.tipsLabel.move(47, 110)
        self.viewLayout.addWidget(self.lineEdit)
        self.viewLayout.addWidget(self.tipsLabel)

        # 重写底部按钮
        self.yesButton.clicked.connect(lambda: self.submit_date("ok"))
        self.cancelButton.clicked.connect(lambda: self.submit_date("canel"))

    def submit_date(self, str):
        self.flag = str
        self.close()

    def getflag(self):
        return self.flag


def tree_to_list(Tree):
    """树结构转列表结构"""
    list = []
    line = []
    line.append(Tree)
    while len(line) > 0:
        _node = line.pop(0)
        list.append(_node)
        if len(_node.children) > 0:
            for item in _node.children:
                line.append(item)
    return list


class SelectWidget(QWidget):
    """通用下拉选框"""

    selectedDateChanged = pyqtSignal(Data)

    def __init__(self, title: str, dataList=None, parent=None):
        super().__init__(parent)
        self.selectlabel = QLabel(f"{title}:", self)
        self.selectlabel.setFixedWidth(100)
        self.selectlabel.setStyleSheet("QLabel{font: 12px 'Microsoft YaHei';}")
        self._comboBox = ComboBox(self)
        self.items = dataList
        for item in self.items:
            self._comboBox.addItem(item.name, userData=item)
        self._comboBox.setCurrentIndex(0)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.selectlabel)
        self.layout.addWidget(self._comboBox)
        self.setContentsMargins(0, 0, 0, 0)
        self._comboBox.currentIndexChanged.connect(self.dateChanged)

    def getCurrentValue(self):
        """获取当前选项值"""
        return self._comboBox.currentData()

    def setValue(self, value):
        """设置选项的值"""
        self._comboBox.setCurrentIndex(self._comboBox.findData(value))

    def updateSelectList(self, datelist):
        """更新所有选项"""
        self._comboBox.clear()
        for item in datelist:
            if isinstance(item, SpaceCorrelation):
                self._comboBox.addItem(str(item), userData=item)
            else:
                self._comboBox.addItem(item.name, userData=item)
        if len(datelist) > 0:
            self.selectedDateChanged.emit(self._comboBox.currentData())

    def dateChanged(self, _):
        """选择的值变化的时候,发出信号"""
        self.selectedDateChanged.emit(self._comboBox.currentData())


class InputWidget(QWidget):
    """输入实体名称的输入框"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.inputlabel = QLabel(f"{title}:", self)
        self.inputlabel.setFixedWidth(100)
        self.inputlabel.setStyleSheet("QLabel{font: 12px 'Microsoft YaHei';}")
        self._inputBox = LineEdit(self)
        self._inputBox.setClearButtonEnabled(True)
        self._inputBox.setMinimumWidth(200)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.inputlabel)
        self.layout.addWidget(self._inputBox)
        self.setContentsMargins(0, 0, 0, 0)

    def gettext(self):
        """获取输入框中的值"""
        return self._inputBox.text()


class EntityCreationDialog(MessageBoxBase):
    """创建 Project Subject DTBModel DTB 弹窗选择关联的实体"""

    def __init__(self, title: str, type="", project: Project = None, parent=None):
        super().__init__(parent=parent)
        self.flag = ""
        self.titleLabel = SubtitleLabel(title)
        self.titleLabel.setContentsMargins(0, 0, 0, 20)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.setSpacing(0)

        # Project 下拉菜单
        project_select_list = tree_to_list(get_workspace())
        self.project_selector = SelectWidget("Project", dataList=project_select_list)
        if not project == None:
            self.project_selector.setValue(project)

        # subject 下拉菜单
        subject_select_list = []
        if project == None:
            subject_select_list = get_workspace().available_subjects()
        else:
            subject_select_list = project.available_subjects()
        self.subject_selector = SelectWidget("Subject", dataList=subject_select_list)

        # Atlas 下拉菜单
        atlas_select_list = get_workspace().atlases
        self.atlas_selector = SelectWidget("Atlas", dataList=atlas_select_list)

        # dynamicModel 下拉菜单
        dynamics_select_list = get_workspace().dynamics
        self.dynamicModel_selector = SelectWidget(
            "Dynamic Model", dataList=dynamics_select_list
        )

        # DTBModel 下拉菜单
        dtb_model_select_list = []
        if project == None:
            dtb_model_select_list = get_workspace().available_models()
        else:
            dtb_model_select_list = project.available_models()
        self.dtbModel_selector = SelectWidget(
            "DTB Model", dataList=dtb_model_select_list
        )

        # connectivity 连接矩阵下拉菜单
        connectivity_select_list = []
        self.connectivity_selector = SelectWidget(
            "Connectivity", dataList=connectivity_select_list
        )
        default_subject = self.subject_selector.getCurrentValue()
        if not default_subject == None:
            self.updateConnectivityList(default_subject)

        # name 输入框
        self.lineEdit = InputWidget("Name")

        # 表单动态联动
        self.project_selector.selectedDateChanged.connect(
            self.updateSubjectAndDTBModelList
        )
        self.subject_selector.selectedDateChanged.connect(self.updateConnectivityList)

        self.viewLayout.addWidget(self.project_selector)
        self.viewLayout.addWidget(self.subject_selector)
        self.viewLayout.addWidget(self.atlas_selector)
        self.viewLayout.addWidget(self.dynamicModel_selector)
        self.viewLayout.addWidget(self.dtbModel_selector)
        self.viewLayout.addWidget(self.connectivity_selector)
        self.viewLayout.addWidget(self.lineEdit)

        # 重写底部按钮
        self.yesButton.clicked.connect(lambda: self.submit_date("ok"))
        self.cancelButton.clicked.connect(lambda: self.submit_date("canel"))
        # 不同窗口控制不同控件的显隐
        if type == "Project" or type == "Subject":
            self.project_selector.show()
            self.subject_selector.hide()
            self.atlas_selector.hide()
            self.dtbModel_selector.hide()
            self.dynamicModel_selector.hide()
            self.connectivity_selector.hide()
        if type == "DTBModel":
            self.project_selector.show()
            self.subject_selector.hide()
            self.atlas_selector.show()
            self.dtbModel_selector.hide()
            self.dynamicModel_selector.show()
            self.connectivity_selector.hide()
        if type == "DTB":
            self.project_selector.show()
            self.subject_selector.show()
            self.atlas_selector.hide()
            self.dtbModel_selector.show()
            self.dynamicModel_selector.hide()
            self.connectivity_selector.show()

    def submit_date(self, str):
        # 标记按钮的点击，关闭窗口
        self.flag = str
        self.close()

    def getflag(self):
        # 获取按钮标记
        return self.flag

    def getData(self, type: str):
        """外部控件根据类型获取用户输入的信息"""
        if type == "Project":
            return self.project_selector.getCurrentValue()
        if type == "Subject":
            return self.subject_selector.getCurrentValue()
        if type == "Atlas":
            return self.atlas_selector.getCurrentValue()
        if type == "DTBModel":
            return self.dtbModel_selector.getCurrentValue()
        if type == "DynamicModel":
            return self.dynamicModel_selector.getCurrentValue()
        if type == "Connectivity":
            return self.connectivity_selector.getCurrentValue()

    def updateSubjectAndDTBModelList(self, project: Project):
        """选择不同的Project的时候，Subject列表和 DTB model列表会进行改变"""
        self.dtbModel_selector.updateSelectList(project.available_models())
        self.subject_selector.updateSelectList(project.available_subjects())

    def updateConnectivityList(self, subject: Subject):
        """选择不同的 Subject 的时候，connectivity列表会进行改变"""
        connectivityitems = []
        for _, value in subject.data.items():
            if isinstance(value, SpaceCorrelation):
                connectivityitems.append(value)
        self.connectivity_selector.updateSelectList(connectivityitems)


def dialog_workspace(parent=None):
    """新建 Workspace 弹窗

    Parameters
    ----------
    parent :
        父级窗口
    """
    title = "Please name your Workspace:"
    w = WorkspaceInputDialog(title, parent)
    res = False
    w.exec()
    if w.getflag() == "canel":
        res = "canel"
    else:
        name = w.lineEdit.text().strip()
        if re.match("^[0-9_a-zA-Z]{1,20}$", name):
            res = name
    return res
