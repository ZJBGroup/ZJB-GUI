from PyQt5.QtCore import QEasingCurve, Qt, pyqtSignal
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    FlowLayout,
    FluentIcon,
    LineEdit,
    PrimaryPushButton,
    SmoothScrollArea,
    SubtitleLabel,
    ToolTipFilter,
    ToolTipPosition,
    TransparentPushButton,
    TransparentToolButton,
)

from ..common.utils import show_error


def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


class ValueEditor(CardWidget):
    """用于添加脑区的编辑器"""

    addStimulationValueSignal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.TitleLabel = SubtitleLabel(self)
        self.TitleLabel.setObjectName("TitleLabel")
        self.TitleLabel.setText("Selected Region")

        self.numlabel = BodyLabel("-")
        self.numlabel.setWordWrap(True)
        self.regionlabel = BodyLabel("-")
        self.regionlabel.setWordWrap(True)
        self.subregionlabel = BodyLabel("-")
        self.subregionlabel.setWordWrap(True)
        self.anatomiclabel = BodyLabel("-")
        self.anatomiclabel.setWordWrap(True)
        self.valueEdit = LineEdit()

        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.formLayout.addRow(BodyLabel("Brain Num:"), self.numlabel)
        self.formLayout.addRow(BodyLabel("Region:"), self.regionlabel)
        self.formLayout.addRow(BodyLabel("Subregion:"), self.subregionlabel)
        self.formLayout.addRow(BodyLabel("Anat-profile:"), self.anatomiclabel)
        self.valuelabel = BodyLabel("Value:")
        self.valuelabel.installEventFilter(
            ToolTipFilter(self.valuelabel, 200, ToolTipPosition.LEFT)
        )
        self.valuelabel.setToolTip("Enter a number between -1 and 1")
        self.formLayout.addRow(self.valuelabel, self.valueEdit)
        self.add_btn = TransparentPushButton("ADD", icon=FluentIcon.ADD_TO)
        self.add_btn.clicked.connect(self.addfunc)

        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(10, 5, 10, 15)
        self._layout.addWidget(self.TitleLabel)
        self._layout.addLayout(self.formLayout)
        self._layout.addWidget(self.add_btn)

    def setValue(self, list, value=None):
        """设置模块中的值"""
        self.numlabel.setText(list[0])
        self.regionlabel.setText(list[1])
        self.subregionlabel.setText(list[2])
        self.anatomiclabel.setText(list[3])
        self.valueEdit.setText(value)

    def getValue(self):
        """获取模块中的值"""
        valuelist = []
        valuelist.append(self.numlabel.text())
        valuelist.append(self.regionlabel.text())
        valuelist.append(self.subregionlabel.text())
        valuelist.append(self.anatomiclabel.text())
        valuelist.append(self.valueEdit.text())
        return valuelist

    def addfunc(self):
        """点击 add 按钮，新增对应脑区的刺激值"""
        _list = self.getValue()
        if not _list[0] == "-" and not _list[4] == "":
            if not is_float(_list[4]):
                show_error("wrong value", self.parent().parent())
                return
            if float(_list[4]) > 1.0 or float(_list[4]) < -1.0:
                show_error("Enter a number between -1 and 1", self.parent().parent())
                return
            self.addStimulationValueSignal.emit(self.getValue())
            self.setValue(["-", "-", "-", "-"])


class ValueItem(CardWidget):
    deleteValueItemSignal = pyqtSignal(str)

    def __init__(self, valuelist, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self._num = valuelist[0]
        self._region = valuelist[1]
        self._value = valuelist[4]
        self.numlabel = BodyLabel(self._num)
        self.numlabel.setFixedWidth(30)
        self.regionlabel = BodyLabel(f"{self._region}:")
        self.regionlabel.setFixedWidth(90)
        self.valuelabel = BodyLabel(self._value)
        self.valuelabel.setFixedWidth(50)
        self._btn = TransparentToolButton(FluentIcon.DELETE)
        self._btn.clicked.connect(self.deleteItem)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(15, 5, 5, 5)
        self._layout.addWidget(self.numlabel)
        self._layout.addWidget(self.regionlabel)
        self._layout.addWidget(self.valuelabel)
        self._layout.addWidget(self._btn)

    @property
    def regionNum(self):
        return self._num

    @property
    def regionName(self):
        return self._region

    @property
    def stimulationValue(self):
        return self._value

    def deleteItem(self):
        self.deleteValueItemSignal.emit(self._num)


class ValueList(SmoothScrollArea):
    """已添加的刺激值的脑区列表"""

    deleteViewValueSignal = pyqtSignal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName(text.replace(" ", "_"))

        # 流动布局
        self.list_layout = FlowLayout(needAni=True)
        self.list_layout.setAnimation(250, QEasingCurve.Type.OutQuad)
        self.list_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动布局相关
        self.list_layout_container = QWidget()
        self.list_layout_container.setLayout(self.list_layout)
        self.container = QWidget(self)
        self.setStyleSheet("QWidget{background-color: transparent;border:none;}")
        self.setWidget(self.container)
        self.setWidgetResizable(True)

        self.TitleLabel = SubtitleLabel(self)
        self.TitleLabel.setObjectName("ValueList")
        self.TitleLabel.setText("ValueList:")

        self._layout = QVBoxLayout(self.container)
        self._layout.addWidget(self.TitleLabel)
        self._layout.addWidget(self.list_layout_container)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.setContentsMargins(0, 10, 0, 0)

    def _addCard(self, item: list):
        """添加一个刺激值

        Parameters
        ----------
        item : list
            item[0] brain num
            item[4] stimulation value
        """
        for i in range(self.list_layout.count()):
            _item = self.list_layout.itemAt(i)
            if item[0] == _item.widget().regionNum:
                self.list_layout.takeAt(i)
                _item.widget().deleteLater()
                break
        card = ValueItem(item)
        card.deleteValueItemSignal.connect(self._deleteCard)
        self.list_layout.addWidget(card)

    def _deleteCard(self, region_num):
        """
        删除一个脑区的刺激值
        :param: region_name: 脑区名称
        """
        for i in range(self.list_layout.count()):
            item = self.list_layout.itemAt(i)
            if region_num == item.widget().regionNum:
                self.list_layout.takeAt(i)
                item.widget().deleteLater()
                break
        self.list_layout.setGeometry(self.list_layout.geometry())
        self.deleteViewValueSignal.emit(region_num)


class StimulationValuePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUi()
        self.value_editor_widget.addStimulationValueSignal.connect(self.addStimulation)

    def _setupUi(self):
        self.setObjectName("Brain_Value_Panel")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(270)
        # 编辑脑区信息的编辑器
        self.value_editor_widget = ValueEditor(self)
        self.value_editor_widget.setObjectName("value_editor_widget")
        # 已经添加的刺激区域
        self.value_list_widget = ValueList("valuelist")
        self.value_list_widget.setObjectName("value_list_widget")
        # 创建控件分布的按钮
        self.create_btn = PrimaryPushButton("Create", icon=FluentIcon.ADD)
        self.create_btn.setObjectName("create_btn")

        self.main_layout.addWidget(self.value_editor_widget)
        self.main_layout.addWidget(self.value_list_widget)
        self.main_layout.addWidget(self.create_btn)

    def addStimulation(self, list):
        """往列表区域增加一个刺激值"""
        self.value_list_widget._addCard(list)
