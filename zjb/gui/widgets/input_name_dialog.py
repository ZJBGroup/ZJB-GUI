import re

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget
from qfluentwidgets import CaptionLabel, ComboBox, Dialog, LineEdit
from zjb.main.manager.workspace import Workspace

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
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.selectlabel = QLabel(f"{title}:", self)
        self.selectlabel.setFixedWidth(100)
        self.selectlabel.setStyleSheet("QLabel{font: 12px 'Microsoft YaHei';}")
        all_project: Workspace = tree_to_list(get_workspace())

        self._comboBox = ComboBox(self)
        items = []
        if title == "Project":
            for _project in all_project:
                items.append(_project)

        if title == "Subject":
            for _project in all_project:
                for _item in _project.subjects:
                    items.append(_item)

        if title == "Dynamic Model":
            for _item in get_workspace().dynamics:
                items.append(_item)

        if title == "DTB Model":
            for _project in all_project:
                for _item in _project.models:
                    items.append(_item)

        for item in items:
            self._comboBox.addItem(item.name, userData=item)

        self._comboBox.setCurrentIndex(0)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.selectlabel)
        self.layout.addWidget(self._comboBox)
        self.setContentsMargins(15, 00, 15, 00)
        self.layout.setSpacing(5)


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


class DTBModelInputDialog(Dialog):
    """创建DTBModel 及DTB时，弹窗选择关联的实体"""

    def __init__(self, title: str, content="", parent=None):
        super().__init__(title, content=content, parent=parent)
        self.setTitleBarVisible(False)
        self.contentLabel.hide()

        # Project 下拉菜单
        self.project_selector = SelectWidget("Project")

        # subject 下拉菜单
        self.subject_selector = SelectWidget("Subject")

        # dynamicModel 下拉菜单
        self.dynamicModel_selector = SelectWidget("Dynamic Model")

        # DTBModel 下拉菜单
        self.dtbModel_selector = SelectWidget("DTB Model")

        # 输入框
        self.lineEdit = InputWidget("Name")

        self.vBoxLayout.insertWidget(2, self.project_selector, 1)
        self.vBoxLayout.insertWidget(3, self.subject_selector, 1)
        self.vBoxLayout.insertWidget(4, self.dynamicModel_selector, 1)
        self.vBoxLayout.insertWidget(5, self.dtbModel_selector, 1)
        self.vBoxLayout.insertWidget(6, self.lineEdit, 2)

        if content == "Project" or content == "Subject":
            self.project_selector.show()
            self.subject_selector.hide()
            self.dtbModel_selector.hide()
            self.dynamicModel_selector.hide()
        if content == "DTBModel":
            self.project_selector.hide()
            self.subject_selector.show()
            self.dtbModel_selector.hide()
            self.dynamicModel_selector.show()
        if content == "DTB":
            self.subject_selector.show()
            self.project_selector.hide()
            self.dtbModel_selector.show()
            self.dynamicModel_selector.hide()

    def getData(self, type: str):
        if type == "Project":
            return self.project_selector._comboBox.currentData()
        if type == "Subject":
            return self.subject_selector._comboBox.currentData()
        if type == "DTBModel":
            return self.dtbModel_selector._comboBox.currentData()
        if type == "DynamicModel":
            return self.dynamicModel_selector._comboBox.currentData()


def show_dialog(parent, tag: str):
    """配置弹窗并显示，用户输入符合标准的名称后将其返回"""
    if tag == "workspace":
        title = "Please name your Workspace:"
        content = "\n| \n| \n| \n| \n|"
        w = WorkspaceInputDialog(title, content)
        if w.exec():
            str = w.lineEdit.text()
            res = re.search("^\w{3,20}$", str)
            if not res:
                show_error("Invalid name! ", parent)
                return False
            else:
                return str
        else:
            return False

    if tag == "Project":
        title = "Choose a parent Project \nAnd name your Project:"
        w = DTBModelInputDialog(title, "Project")
        if w.exec():
            name = w.lineEdit.gettext()
            res = re.search("^\w{3,20}$", name)
            if not res:
                show_error("Invalid name! ", parent)
                return False
            else:
                return {"project": w.getData("Project"), "name": name}
        else:
            return False

    if tag == "Subject":
        title = "Choose a parent Project \nAnd name your Subject:"
        w = DTBModelInputDialog(title, "Subject")
        if w.exec():
            name = w.lineEdit.gettext()
            res = re.search("^\w{3,20}$", name)
            if not res:
                show_error("Invalid name! ", parent)
            else:
                return {"Project": w.getData("Project"), "name": name}
        else:
            return False

    if tag == "DTBModel":
        title = "Choose a Subject and a Dynamic Model \nAnd name your DTBModel:"
        w = DTBModelInputDialog(title, "DTBModel")
        if w.exec():
            name = w.lineEdit.gettext()
            res = re.search("^\w{3,20}$", name)
            if not res:
                show_error("Invalid name! ", parent)
                return False
            else:
                return {
                    "Subject": w.getData("Subject"),
                    "DynamicModel": w.getData("DynamicModel"),
                    "name": name,
                }
        else:
            return False

    if tag == "DTB":
        title = "Choose a Subject and a DTB Model\nAnd name your DTB:"
        w = DTBModelInputDialog(title, "DTB")
        if w.exec():
            name = w.lineEdit.gettext()
            res = re.search("^\w{3,20}$", name)
            if not res:
                show_error("Invalid name! ", parent)
                return False
            else:
                return {
                    "Subject": w.getData("Subject"),
                    "DTBModel": w.getData("DTBModel"),
                    "name": name,
                }
        else:
            return False
