import re

from qfluentwidgets import CaptionLabel, Dialog, LineEdit

from ..common.utils import show_error


class InputDialog(Dialog):
    """输入工作空间名称的弹窗类"""

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content=content, parent=parent)
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
        self.setTitleBarVisible(False)


def show_dialog(parent):
    """配置弹窗并显示，用户输入符合标准的名称后将其返回"""
    title = "Please name your workspace:"
    content = "\n| \n| \n| \n| \n|"
    w = InputDialog(title, content)
    if w.exec():
        str = w.lineEdit.text()
        res = re.search("^\w{3,20}$", str)
        if not res:
            show_error("Invalid name! ", parent)
        else:
            return str
    else:
        return False
