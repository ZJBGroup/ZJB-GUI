from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    FluentIcon,
    LineEdit,
    MessageBoxBase,
    PushButton,
    SubtitleLabel,
    TransparentToolButton,
)

from zjb.main.api import (
    Atlas,
    DTBModel,
    GaussianStimulus,
    NCyclePulseStimulus,
    PulseStimulus,
    SinusoidStimulus,
)
from zjb.main.dtb.utils import expression2unicode

from .._global import GLOBAL_SIGNAL, get_workspace
from ..pages.stimulation_space_page import StimulationSpacePage


def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


class BaseForm(QWidget):
    """动态表单"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.formLayout = QFormLayout(self)
        self.formLayout.setContentsMargins(0, 0, 0, 0)

    def getFormData(slef): ...


class GaussianForm(BaseForm):
    """Gaussian 刺激的动态表单"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ampEdit = LineEdit(self)
        self.ampEdit.setText("1")
        self.formLayout.addRow(BodyLabel("amp:"), self.ampEdit)
        self.muEdit = LineEdit(self)
        self.muEdit.setText("2")
        self.formLayout.addRow(BodyLabel("mu:"), self.muEdit)
        self.sigmaEdit = LineEdit(self)
        self.sigmaEdit.setText("0.5")
        self.formLayout.addRow(BodyLabel("sigma:"), self.sigmaEdit)
        self.offsetEdit = LineEdit(self)
        self.offsetEdit.setText("0")
        self.formLayout.addRow(BodyLabel("offset:"), self.offsetEdit)

    def setFormValue(self, data):
        """设置表单数据"""
        [value1, value2, value3, value4] = data
        self.ampEdit.setText(str(value1))
        self.muEdit.setText(str(value2))
        self.sigmaEdit.setText(str(value3))
        self.offsetEdit.setText(str(value4))

    def getFormData(self):
        """获取表单数据"""
        if (
            is_float(self.ampEdit.text())
            and is_float(self.muEdit.text())
            and is_float(self.sigmaEdit.text())
            and is_float(self.offsetEdit.text())
        ):
            return {
                "amp": float(self.ampEdit.text()),
                "mu": float(self.muEdit.text()),
                "sigma": float(self.sigmaEdit.text()),
                "offset": float(self.offsetEdit.text()),
            }
        else:
            return {
                "amp": "",
                "mu": "",
                "sigma": "",
                "offset": "",
            }


class PulseForm(BaseForm):
    """Pulse 刺激的动态表单"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ampEdit = LineEdit(self)
        self.ampEdit.setText("1")
        self.formLayout.addRow(BodyLabel("amp:"), self.ampEdit)
        self.startEdit = LineEdit(self)
        self.startEdit.setText("1")
        self.formLayout.addRow(BodyLabel("start:"), self.startEdit)
        self.widthEdit = LineEdit(self)
        self.widthEdit.setText("1")
        self.formLayout.addRow(BodyLabel("width:"), self.widthEdit)

    def setFormValue(self, data):
        """设置表单数据"""
        [value1, value2, value3] = data
        self.ampEdit.setText(str(value1))
        self.startEdit.setText(str(value2))
        self.widthEdit.setText(str(value3))

    def getFormData(self):
        """获取表单数据"""
        if (
            is_float(self.ampEdit.text())
            and is_float(self.startEdit.text())
            and is_float(self.widthEdit.text())
        ):
            return {
                "amp": float(self.ampEdit.text()),
                "start": float(self.startEdit.text()),
                "width": float(self.widthEdit.text()),
            }
        else:
            return {
                "amp": "",
                "start": "",
                "width": "",
            }


class NCyclePulseForm(PulseForm):
    """NCyclePulse 刺激的动态表单"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.periodEdit = LineEdit(self)
        self.periodEdit.setText("2")
        self.formLayout.addRow(BodyLabel("period:"), self.periodEdit)
        self.countEdit = LineEdit(self)
        self.countEdit.setText("0")
        self.formLayout.addRow(BodyLabel("count:"), self.countEdit)

    def setFormValue(self, data):
        """设置表单数据"""
        [value1, value2, value3, value4, value5] = data
        self.ampEdit.setText(str(value1))
        self.startEdit.setText(str(value2))
        self.widthEdit.setText(str(value3))
        self.periodEdit.setText(str(value4))
        self.countEdit.setText(str(value5))

    def getFormData(self):
        """获取表单数据"""
        if (
            is_float(self.ampEdit.text())
            and is_float(self.startEdit.text())
            and is_float(self.widthEdit.text())
            and is_float(self.periodEdit.text())
            and is_float(self.countEdit.text())
        ):
            return {
                "amp": float(self.ampEdit.text()),
                "start": float(self.startEdit.text()),
                "width": float(self.widthEdit.text()),
                "period": float(self.periodEdit.text()),
                "count": int(self.countEdit.text()),
            }
        else:
            return {
                "amp": "",
                "start": "",
                "width": "",
                "period": "",
                "count": "",
            }


class SinusoidForm(BaseForm):
    """Sinusoid 刺激的动态表单"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ampEdit = LineEdit(self)
        self.ampEdit.setText("1")
        self.formLayout.addRow(BodyLabel("amp:"), self.ampEdit)
        self.freqEdit = LineEdit(self)
        self.freqEdit.setText("1")
        self.formLayout.addRow(BodyLabel("freq:"), self.freqEdit)
        self.phaseEdit = LineEdit(self)
        self.phaseEdit.setText("0")
        self.formLayout.addRow(BodyLabel("phase:"), self.phaseEdit)
        self.offsetEdit = LineEdit(self)
        self.offsetEdit.setText("0")
        self.formLayout.addRow(BodyLabel("offset:"), self.offsetEdit)

    def setFormValue(self, data):
        """设置表单数据"""
        [value1, value2, value3, value4] = data
        self.ampEdit.setText(str(value1))
        self.freqEdit.setText(str(value2))
        self.phaseEdit.setText(str(value3))
        self.offsetEdit.setText(str(value4))

    def getFormData(self):
        """获取表单数据"""
        if (
            is_float(self.ampEdit.text())
            and is_float(self.freqEdit.text())
            and is_float(self.phaseEdit.text())
            and is_float(self.offsetEdit.text())
        ):
            return {
                "amp": float(self.ampEdit.text()),
                "freq": float(self.freqEdit.text()),
                "phase": float(self.phaseEdit.text()),
                "offset": float(self.offsetEdit.text()),
            }
        else:
            return {
                "amp": "",
                "freq": "",
                "phase": "",
                "offset": "",
            }


class SpaceInputWidget(QWidget):
    """添加刺激空间分布的条目"""

    def __init__(self, atlas: Atlas, parent=None):
        super().__init__(parent)
        self._atlas = atlas
        self._workspace = get_workspace()
        self._subject = None
        self._edit_space = None
        self._inputBox = LineEdit(self)
        self._inputBox.setDisabled(True)
        self._inputBox.setClearButtonEnabled(True)
        self._inputBox.setMinimumWidth(200)
        self._btn = TransparentToolButton(FluentIcon.ADD_TO)
        self._btn.clicked.connect(self.btnclick)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self._inputBox)
        self.layout.addWidget(self._btn)
        self.layout.setContentsMargins(0, 0, 0, 0)

        select_atlas_name = self._atlas.name
        for subject in self._workspace.subjects:
            if select_atlas_name == "AAL90":
                if subject.name == "cortex_80k":
                    self._subject = subject
                    break
            else:
                if subject.name == "fsaverage":
                    self._subject = subject
                    break

        if self._edit_space:
            self._btn.setIcon(FluentIcon.EDIT)

    def btnclick(self):
        GLOBAL_SIGNAL.requestAddPage.emit(
            "stimulation",
            lambda _: StimulationSpacePage(
                self._atlas, self._subject, self._edit_space
            ),
        )

    def settext(self, _str):
        """往输入框中输入值"""
        self._inputBox.setText(_str)

    def setspace(self, spacelist: list):
        """设置编辑回显的空间分布列表"""
        self._edit_space = spacelist
        self._btn.setIcon(FluentIcon.EDIT)


class StimulationDialog(MessageBoxBase):
    """添加刺激得弹窗的弹窗"""

    deleteStimulationSignal = pyqtSignal(str)

    def __init__(self, title: str, atlas: Atlas, model: DTBModel, data, parent=None):
        super().__init__(parent=parent)
        self.flag = ""
        self._space_value = None
        self._atlas = atlas
        self._model = model
        self._edit_data = data  # 回显数据
        self.titleLabel = SubtitleLabel(title)
        self.titleLabel.setContentsMargins(0, 0, 0, 20)
        self.viewLayout.addWidget(self.titleLabel)
        self.formLayout = QFormLayout()
        self.viewLayout.addLayout(self.formLayout)

        # 类型下拉框
        type_select_list = ["Gaussian", "NCyclePulse", "Pulse", "Sinusoid"]
        self.type_comboBox = ComboBox(self)
        for item in type_select_list:
            self.type_comboBox.addItem(str(item), userData=item)
        self.type_comboBox.setCurrentIndex(0)
        self.formLayout.addRow(BodyLabel("Type:"), self.type_comboBox)
        self.type_comboBox.currentIndexChanged.connect(self._updateForm)
        # 默认的 Gaussian 表单
        self.formWidget = GaussianForm(self)
        self.formLayout.addRow(BodyLabel(""), self.formWidget)
        # 刺激空间分布
        self.spaceEdit = SpaceInputWidget(self._atlas, self)
        self.formLayout.addRow(BodyLabel("Space:"), self.spaceEdit)
        # 参数下拉框
        self.param_select_list = [key for key in self._model.dynamics.parameters]
        self.param_comboBox = ComboBox(self)
        for item in self.param_select_list:
            self.param_comboBox.addItem(
                str(expression2unicode(item, False)), userData=item
            )
        self.param_comboBox.setCurrentIndex(0)
        self.formLayout.addRow(BodyLabel("Param:"), self.param_comboBox)
        # 重写底部按钮
        self.yesButton.clicked.connect(lambda: self.submit_date("ok"))
        self.cancelButton.clicked.connect(lambda: self.submit_date("canel"))
        GLOBAL_SIGNAL.stimulationSpaceCreated.connect(self.setSpaceValue)

        if self._edit_data:
            self.editView(self._edit_data)
            self.param_comboBox.setDisabled(True)  # 禁用参数框

            self.del_btn = PushButton("Delete", icon=FluentIcon.DELETE)
            self.del_btn.setObjectName("del_btn")
            self.del_btn.clicked.connect(self.deleteStimulation)
            self.formLayout.addRow(self.del_btn)

    def deleteStimulation(self):
        """点击删除按钮"""
        self.deleteStimulationSignal.emit(self._edit_data[0])
        self.close()

    def editView(self, _data):
        """编辑数据回显

        Parameters
        ----------
        _data : list
            长度为2 第一个为参数，第二个为刺激
        """
        [_param, _stimulus] = _data
        # 参数回显
        i = 0
        for _item in self.param_select_list:
            if _item == _param:
                break
            i = i + 1
        self.param_comboBox.setCurrentIndex(i)
        # 刺激类型及对应刺激参数回显
        if isinstance(_stimulus, GaussianStimulus):
            self.type_comboBox.setCurrentIndex(0)
            self._updateForm()
            self.formWidget.setFormValue(
                [_stimulus.amp, _stimulus.mu, _stimulus.sigma, _stimulus.offset]
            )
        elif isinstance(_stimulus, NCyclePulseStimulus):
            self.type_comboBox.setCurrentIndex(1)
            self._updateForm()
            self.formWidget.setFormValue(
                [
                    _stimulus.amp,
                    _stimulus.start,
                    _stimulus.width,
                    _stimulus.period,
                    _stimulus.count,
                ]
            )
        elif isinstance(_stimulus, PulseStimulus):
            self.type_comboBox.setCurrentIndex(2)
            self._updateForm()
            self.formWidget.setFormValue(
                [_stimulus.amp, _stimulus.start, _stimulus.width]
            )
        elif isinstance(_stimulus, SinusoidStimulus):
            self.type_comboBox.setCurrentIndex(3)
            self._updateForm()
            self.formWidget.setFormValue(
                [_stimulus.amp, _stimulus.freq, _stimulus.phase, _stimulus.offset]
            )
        # 空间分布回显
        self.setSpaceValue(None, spacelist=list(_stimulus.space))
        self.spaceEdit.setspace(list(_stimulus.space))

    def _updateForm(self):
        """根据刺激类型更新动态表单"""
        self.formLayout.removeRow(self.formWidget)
        if self.type_comboBox.currentData() == "Gaussian":
            self.formWidget = GaussianForm(self)
        elif self.type_comboBox.currentData() == "NCyclePulse":
            self.formWidget = NCyclePulseForm(self)
        elif self.type_comboBox.currentData() == "Pulse":
            self.formWidget = PulseForm(self)
        elif self.type_comboBox.currentData() == "Sinusoid":
            self.formWidget = SinusoidForm(self)
        self.formLayout.insertRow(1, "", self.formWidget)

    def setSpaceValue(self, _, spacelist):
        """接收刺激空间布局得值

        Parameters
        ----------
        spacelist : list
            刺激的空间布局
        """
        self._space_value = spacelist
        self.spaceEdit.settext(str(type(spacelist)))
        self.spaceEdit.setspace(spacelist)

    def getData(self):
        """根据用户输入的值，建立一个刺激对象并返回"""
        _data = dict(
            **{"type": self.type_comboBox.currentData()},
            **{"param": self.param_comboBox.currentData()},
            **{
                "valuelist": dict(
                    **{"space": self._space_value},
                    **self.formWidget.getFormData(),
                )
            },
        )
        return _data

    def submit_date(self, str):
        """标记按钮的点击，关闭窗口"""
        self.flag = str

    def getflag(self):
        """获取按钮标记"""
        return self.flag
