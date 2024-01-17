import re

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget
from qfluentwidgets import (CaptionLabel, ComboBox, LineEdit, MessageBoxBase,
                            SubtitleLabel)
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

        # 底部按钮
        self.yesButton.clicked.connect(lambda: self.submit_date("ok"))
        self.cancelButton.clicked.connect(lambda: self.submit_date("canel"))

    def submit_date(self, str):
        self.flag = str
        self.close()

    def getflag(self):
        return self.flag


class SelectWidget(QWidget):
    """通用下拉选框"""

    selectedDateChanged = pyqtSignal(object)

    def __init__(self, title: str, dataList=None, parent=None):
        super().__init__(parent)
        self.selectlabel = QLabel(f"{title}:", self)
        self.selectlabel.setFixedWidth(100)
        self.selectlabel.setStyleSheet("QLabel{font: 12px 'Microsoft YaHei';}")
        self._comboBox = ComboBox(self)
        self.items = dataList
        for item in self.items:
            if hasattr(item, "name"):
                self._comboBox.addItem(item.name, userData=item)
            else:
                self._comboBox.addItem(str(item), userData=item)
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
            if isinstance(item, dict):
                self._comboBox.addItem(item["name"], userData=item["value"])
            elif not hasattr(item, "name"):
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

    def settext(self, str):
        """往输入框中输入值"""
        self._inputBox.setText(str)


class EntityCreationBase(MessageBoxBase):
    """新建 Project 和新建 Subject 的弹窗"""

    def __init__(self, title: str, type="", project: Project = None, parent=None):
        super().__init__(parent=parent)
        self.flag = ""
        self._type = type
        self._project = project
        self.titleLabel = SubtitleLabel(title)
        self.titleLabel.setContentsMargins(0, 0, 0, 20)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.setSpacing(0)

        # name 输入框
        self.lineEdit = InputWidget("Name")

        # Project 下拉菜单
        project_select_list = tree_to_list(get_workspace())
        self.project_selector = SelectWidget("Project", dataList=project_select_list)
        if not project == None:
            self.project_selector.setValue(project)

        self.viewLayout.addWidget(self.lineEdit)
        self.viewLayout.addWidget(self.project_selector)
        # 重写底部按钮
        self.yesButton.clicked.connect(lambda: self.submit_date("ok"))
        self.cancelButton.clicked.connect(lambda: self.submit_date("canel"))

    @property
    def getData(self):
        """外部控件根据类型获取用户输入的信息"""
        return {"Project": self.project_selector.getCurrentValue()}

    def submit_date(self, str):
        """标记按钮的点击，关闭窗口"""
        self.flag = str
        self.close()

    def getflag(self):
        """获取按钮标记"""
        return self.flag


class DTBModelCreationDialog(EntityCreationBase):
    """新建 DTB Model 的弹窗"""

    def __init__(self, title: str, type="", project: Project = None, parent=None):
        super().__init__(title=title, type=type, project=project, parent=parent)

        # Atlas 下拉菜单
        atlas_select_list = get_workspace().atlases
        self.atlas_selector = SelectWidget("Atlas", dataList=atlas_select_list)

        # dynamicModel 下拉菜单
        dynamics_select_list = get_workspace().dynamics
        self.dynamicModel_selector = SelectWidget(
            "Dynamic Model", dataList=dynamics_select_list
        )

        self.viewLayout.addWidget(self.atlas_selector)
        self.viewLayout.addWidget(self.dynamicModel_selector)

    @property
    def getData(self):
        """外部控件根据类型获取用户输入的信息"""
        return {
            "Project": self.project_selector.getCurrentValue(),
            "Atlas": self.atlas_selector.getCurrentValue(),
            "DynamicModel": self.dynamicModel_selector.getCurrentValue(),
        }


class DTBCreationDialog(EntityCreationBase):
    """新建 DTB 的弹窗"""

    def __init__(self, title: str, type="", project: Project = None, parent=None):
        super().__init__(title=title, type=type, project=project, parent=parent)

        # subject 下拉菜单
        subject_select_list = []
        if project == None:
            subject_select_list = get_workspace().available_subjects()
        else:
            subject_select_list = project.available_subjects()
        self.subject_selector = SelectWidget("Subject", dataList=subject_select_list)

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

        self.viewLayout.addWidget(self.subject_selector)
        self.viewLayout.addWidget(self.dtbModel_selector)
        self.viewLayout.addWidget(self.connectivity_selector)

        # 表单动态联动
        self.project_selector.selectedDateChanged.connect(
            self.updateSubjectAndDTBModelList
        )
        self.subject_selector.selectedDateChanged.connect(self.updateConnectivityList)
        self.dtbModel_selector.selectedDateChanged.connect(self.updateDTBModelList)

    @property
    def getData(self):
        """外部控件根据类型获取用户输入的信息"""
        return {
            "Project": self.project_selector.getCurrentValue(),
            "Subject": self.subject_selector.getCurrentValue(),
            "DTBModel": self.dtbModel_selector.getCurrentValue(),
            "Connectivity": self.connectivity_selector.getCurrentValue(),
        }

    def updateSubjectAndDTBModelList(self, project: Project):
        """选择不同的Project的时候，Subject列表和 DTB model列表会进行改变"""
        self.dtbModel_selector.updateSelectList(project.available_models())
        self.subject_selector.updateSelectList(project.available_subjects())
        if not self._type == "DTB":
            self.set_name(False)

    def updateConnectivityList(self, subject: Subject):
        """选择不同的 Subject 的时候，connectivity列表会进行改变"""
        connectivityitems = []
        for key, value in subject.data.items():
            _item = {"name": key, "value": value}
            if isinstance(value, SpaceCorrelation):
                connectivityitems.append(_item)
        self.connectivity_selector.updateSelectList(connectivityitems)
        if self._type == "DTB":
            self.set_name()

    def updateDTBModelList(self):
        """选择不同的 DTB Model 的时候，dtb的名称进行变化"""
        self.set_name()

    def set_name(self, flag=True):
        """设置默认的 DTB 名称"""
        if flag:
            sub_name = self.getData["Subject"]
            model_name = self.getData["DTBModel"]
            if not sub_name == None and not model_name == None:
                self.lineEdit.settext(
                    _generate_key(
                        self.getData["Project"].dtbs,
                        f"{sub_name.name}-{model_name.name}",
                    )
                )
        else:
            self.lineEdit.settext("")


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


def _generate_key(data: list, prefix: str):
    """生成默认的DTB名称

    Parameters
    ----------
    prefix : str
        除了 index 之外的名称字符串
    """
    pattern = re.compile(rf"{prefix}-(\d+)")
    _max = 0
    for item in data:
        if res := pattern.fullmatch(item.name):
            value = int(res.groups()[0])
            if value > _max:
                _max = value
    _max += 1
    return f"{prefix}-{_max}"


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
