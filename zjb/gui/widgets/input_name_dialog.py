import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, ComboBox, Dialog, LineEdit

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


class SelectWidget(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.selectlabel = QLabel(f"{title}:", self)
        self.selectlabel.setFixedWidth(100)
        self.selectlabel.setStyleSheet("QLabel{font: 12px 'Microsoft YaHei';}")

        self._comboBox = ComboBox(self)
        items = []
        if title == "Subject":
            for _item in get_workspace().subjects:
                items.append(_item.name)

        if title == "Dynamic Model":
            for _item in get_workspace().dynamics:
                items.append(_item.name)

        if title == "DTB Model":
            for _item in get_workspace().models:
                items.append(_item.name)

        self._comboBox.addItems(items)
        self._comboBox.setCurrentIndex(0)
        self._comboBox.currentTextChanged.connect(print)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.selectlabel)
        self.layout.addWidget(self._comboBox)
        self.setContentsMargins(15, 00, 15, 00)
        self.layout.setSpacing(5)


class DTBModelInputDialog(Dialog):
    """输入工作空间名称的弹窗类"""

    def __init__(self, title: str, content="", parent=None):
        super().__init__(title, content=content, parent=parent)
        self.setTitleBarVisible(False)
        # self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.hide()

        # subject 下拉菜单
        self.subject_selector = SelectWidget("Subject")

        # dynamicModel 下拉菜单
        self.dynamicModel_selector = SelectWidget("Dynamic Model")

        # DTBModel 下拉菜单
        self.dtbModel_selector = SelectWidget("DTB Model")

        self.vBoxLayout.insertWidget(2, self.subject_selector, 1)
        self.vBoxLayout.insertWidget(3, self.dynamicModel_selector, 1)
        self.vBoxLayout.insertWidget(4, self.dtbModel_selector, 1)

        if content == "DTBModel":
            self.dtbModel_selector.hide()
            self.dynamicModel_selector.show()
        else:
            self.dtbModel_selector.show()
            self.dynamicModel_selector.hide()


def show_dialog(parent, tag: str):
    """配置弹窗并显示，用户输入符合标准的名称后将其返回"""
    if tag == "workspace":
        title = "Please name your workspace:"
        content = "\n| \n| \n| \n| \n|"
        w = WorkspaceInputDialog(title, content)
        if w.exec():
            str = w.lineEdit.text()
            res = re.search("^\w{3,20}$", str)
            if not res:
                show_error("Invalid name! ", parent)
            else:
                return str
        else:
            return False

    if tag == "DTBModel":
        title = "Choose a Subject and a Dynamic Model:"
        w = DTBModelInputDialog(title, "DTBModel")
        if w.exec():
            ...
            # str = w.lineEdit.text()
            # res = re.search("^\w{3,20}$", str)
            # if not res:
            #     show_error("Invalid name! ", parent)
            # else:
            #     return str
        else:
            return False

    if tag == "DTB":
        title = "Choose a Subject and a DTB Model:"
        w = DTBModelInputDialog(title, "DTB")
        if w.exec():
            ...
            # str = w.lineEdit.text()
            # res = re.search("^\w{3,20}$", str)
            # if not res:
            #     show_error("Invalid name! ", parent)
            # else:
            #     return str
        else:
            return False
