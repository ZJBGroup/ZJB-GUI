import re

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget
from qfluentwidgets import CaptionLabel, ComboBox, Dialog, LineEdit, MessageBoxBase
from zjb.dos.data import Data
from zjb.main.api import DTB, DTBModel, Project, SpaceCorrelation, Subject, Workspace

from .._global import get_workspace
from ..common.utils import show_error


class WorkspaceInputDialog(Dialog):
    """输入工作空间名称的弹窗类"""

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content=content, parent=parent)
        self.setTitleBarVisible(False)
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
        self.setContentsMargins(15, 00, 15, 00)
        self.layout.setSpacing(5)
        self._comboBox.currentIndexChanged.connect(self.dateChanged)

    def getCurrentValue(self):
        """获取选项值"""
        return self._comboBox.currentData()

    def setValue(self, value):
        """设置选项的值"""
        self._comboBox.setCurrentIndex(self._comboBox.findData(value))

    def updateSelectList(self, datelist):
        """更新选项列表"""
        self._comboBox.clear()
        for item in datelist:
            if isinstance(item, SpaceCorrelation):
                self._comboBox.addItem(str(item), userData=item)
            else:
                self._comboBox.addItem(item.name, userData=item)

    def dateChanged(self, _):
        """选择的值变化的时候,发出信号"""
        # if isinstance(self._comboBox.currentData(), Project) or isinstance(
        #     self._comboBox.currentData(), Subject
        # ):
        self.selectedDateChanged.emit(self._comboBox.currentData())


class InputWidget(QWidget):
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
        self.setContentsMargins(15, 00, 15, 00)
        self.layout.setSpacing(5)

    def gettext(self):
        return self._inputBox.text()


class EntityCreationDialog(Dialog):
    """创建DTBModel 及DTB时，弹窗选择关联的实体"""

    def __init__(self, title: str, content="", parent=None, project: Project = None):
        super().__init__(title, content=content, parent=parent)
        self.setTitleBarVisible(False)
        self.contentLabel.hide()
        all_project: Workspace = tree_to_list(get_workspace())

        # Project 下拉菜单
        project_select_list = all_project
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

        # 输入框
        self.lineEdit = InputWidget("Name")

        # 选择不同的Project的时候，Subject列表和 DTB model列表会进行改变
        self.project_selector.selectedDateChanged.connect(
            self.updateSubjectAndDTBModelList
        )

        # 选择不同的 Subject 的时候，connectivity列表会进行改变
        self.subject_selector.selectedDateChanged.connect(self.updateConnectivityList)

        self.vBoxLayout.insertWidget(2, self.project_selector, 1)
        self.vBoxLayout.insertWidget(3, self.subject_selector, 1)
        self.vBoxLayout.insertWidget(4, self.atlas_selector, 1)
        self.vBoxLayout.insertWidget(5, self.dynamicModel_selector, 1)
        self.vBoxLayout.insertWidget(6, self.dtbModel_selector, 1)
        self.vBoxLayout.insertWidget(7, self.connectivity_selector, 1)
        self.vBoxLayout.insertWidget(8, self.lineEdit, 2)

        # 不同窗口控制不同控件的显隐
        if content == "Project" or content == "Subject":
            self.project_selector.show()
            self.subject_selector.hide()
            self.atlas_selector.hide()
            self.dtbModel_selector.hide()
            self.dynamicModel_selector.hide()
            self.connectivity_selector.hide()
        if content == "DTBModel":
            self.project_selector.show()
            self.subject_selector.hide()
            self.atlas_selector.show()
            self.dtbModel_selector.hide()
            self.dynamicModel_selector.show()
            self.connectivity_selector.hide()
        if content == "DTB":
            self.project_selector.show()
            self.subject_selector.show()
            self.atlas_selector.hide()
            self.dtbModel_selector.show()
            self.dynamicModel_selector.hide()
            self.connectivity_selector.show()

    #
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
        connectivityitems = []
        print("subject,data", subject.data)
        for _, value in subject.data.items():
            print(value, "0000000000000000000000")
            if isinstance(value, SpaceCorrelation):
                connectivityitems.append(value)
        self.connectivity_selector.updateSelectList(connectivityitems)


def show_dialog(tag: str, project=None):
    """配置弹窗并显示，用户输入符合标准的名称后将其返回"""
    if tag == "workspace":
        title = "Please name your Workspace:"
        content = "\n| \n| \n| \n| \n|"
        w = WorkspaceInputDialog(title, content)
        if w.exec():
            str = w.lineEdit.text()
            res = re.search("^\w{3,20}$", str)
            if not res:
                return False
            else:
                return str
        else:
            return False

    if tag == "Project":
        title = "Choose a parent Project \nAnd name your Project:"
        w = EntityCreationDialog(title, "Project", project=project)
        if w.exec():
            name = w.lineEdit.gettext()
            res = re.search("^\w{3,20}$", name)

            if not res:
                return False
            else:
                return {"Project": w.getData("Project"), "name": name}

        else:
            return False

    if tag == "Subject":
        title = "Choose a parent Project \nAnd name your Subject:"
        w = EntityCreationDialog(title, "Subject", project=project)
        if w.exec():
            name = w.lineEdit.gettext()
            res = re.search("^\w{3,20}$", name)

            if not res:
                return False
            else:
                return {"Project": w.getData("Project"), "name": name}

        else:
            return False

    if tag == "DTBModel":
        title = "Choose an Atlas and a Dynamic Model \nAnd name your DTBModel:"
        w = EntityCreationDialog(title, "DTBModel", project=project)
        if w.exec():
            name = w.lineEdit.gettext()
            res = re.search("^\w{3,20}$", name)

            if (
                res == None
                or w.getData("Atlas") == None
                or w.getData("DynamicModel") == None
            ):
                return False
            else:
                return {
                    "Project": w.getData("Project"),
                    "Atlas": w.getData("Atlas"),
                    "DynamicModel": w.getData("DynamicModel"),
                    "name": name,
                }

        else:
            return False

    if tag == "DTB":
        title = "Choose a Subject and a DTB Model\nAnd name your DTB:"
        w = EntityCreationDialog(title, "DTB", project=project)
        if w.exec():
            name = w.lineEdit.gettext()
            res = re.search("^\w{3,20}$", name)

            if (
                res == None
                or w.getData("Subject") == None
                or w.getData("DTBModel") == None
                or w.getData("Connectivity") == None
            ):
                return False
            else:
                return {
                    "Project": w.getData("Project"),
                    "Subject": w.getData("Subject"),
                    "DTBModel": w.getData("DTBModel"),
                    "Connectivity": w.getData("Connectivity"),
                    "name": name,
                }

        else:
            return False
