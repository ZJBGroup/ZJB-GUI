from functools import partial

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    IconWidget,
    LineEdit,
    PrimaryPushButton,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
    ToolTipFilter,
    ToolTipPosition,
    TransparentPushButton,
    TransparentToolButton,
)

from zjb.main.api import (
    BOLD,
    SOLVER_DICT,
    DTBModel,
    GaussianStimulus,
    Monitor,
    NCyclePulseStimulus,
    PulseStimulus,
    Raw,
    SinusoidStimulus,
    Solver,
    SubSample,
    TemporalAverage,
)
from zjb.main.dtb.utils import expression2unicode

from .._global import GLOBAL_SIGNAL, get_workspace
from ..common.utils import show_error
from ..widgets.dict_editor import KeySetDictEditor
from ..widgets.editor import FloatEditor, IntEditor, LineEditor
from ..widgets.instance_editor import (
    InstanceEditor,
    InstanceEditorAttr,
    InstanceEditorFactory,
)
from ..widgets.list_editor import ListEditor
from ..widgets.stimulation_dialog import StimulationDialog
from .atlas_surface_page import AtlasSurfacePage
from .base_page import BasePage
from .dynamics_page import DynamicsInformationPage


class DTBModelPage(BasePage):
    def __init__(self, model: DTBModel):
        super().__init__(model._gid.str, model.name, FluentIcon.IOT)
        self.model = model

        self._setup_ui()

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 页面信息部分
        self.info_panel = QWidget(self)
        self.info_panel_layout = QHBoxLayout(self.info_panel)
        self.info_panel_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.pageicon = IconWidget(FluentIcon.IOT, self)
        self.pageicon.setFixedSize(140, 140)
        self.info_panel_layout.addWidget(self.pageicon)

        # 信息部分右侧文字及按钮部分
        self.detail_panel = QWidget(self)
        self.detail_panel.setMinimumHeight(40)
        self.detail_panel_layout = QVBoxLayout(self.detail_panel)
        self.detail_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detail_panel_layout.setContentsMargins(30, 0, 0, 0)
        self.detail_panel_layout.addWidget(TitleLabel(self.model.name))

        atlas = self.model.atlas
        btn_atlas = TransparentPushButton(atlas.name, icon=FluentIcon.EDUCATION)
        # FIXME: workspace.subjects[0] may not exist
        btn_atlas.clicked.connect(
            lambda: GLOBAL_SIGNAL.requestAddPage.emit(
                atlas._gid.str,
                lambda _: AtlasSurfacePage(
                    atlas,
                    get_workspace().subjects[0],
                ),
            )
        )

        dynamics = self.model.dynamics
        btn_dynamics = TransparentPushButton(dynamics.name, icon=FluentIcon.ROBOT)
        btn_dynamics.clicked.connect(
            lambda: GLOBAL_SIGNAL.requestAddPage.emit(
                dynamics.name,
                lambda _: DynamicsInformationPage(
                    dynamics.name,
                    dynamics.name + " information",
                    FluentIcon.DEVELOPER_TOOLS,
                    dynamics,
                    0,
                ),
            )
        )

        # 数据按钮布局
        self.detail_button_container = QWidget()
        self.detail_button_layout = QHBoxLayout(self.detail_button_container)
        self.detail_button_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_button_layout.addWidget(btn_atlas)
        self.detail_button_layout.addWidget(btn_dynamics)
        self.detail_panel_layout.addWidget(self.detail_button_container)

        # 按钮组
        self.button_group = QWidget(self)
        self.button_group_layout = QHBoxLayout(self.button_group)
        self.button_group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.button_group_layout.setContentsMargins(0, 20, 0, 0)
        btn_stimulation = PrimaryPushButton(f"stimulation")
        btn_stimulation.setFixedWidth(130)
        btn_stimulation.clicked.connect(self._stimulation_dialog)
        self.button_group_layout.addWidget(btn_stimulation)

        # 添加到布局中
        self.detail_panel_layout.addWidget(self.button_group)
        self.info_panel_layout.addWidget(self.detail_panel)
        self.vBoxLayout.addWidget(self.info_panel)
        self.vBoxLayout.addWidget(SubtitleLabel(f"Detail:"))
        self.scrollArea = SmoothScrollArea(self)
        self.vBoxLayout.addWidget(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        # states
        self.scrollLayout.addWidget(SubtitleLabel("Initial value of state variable:"))
        for state in dynamics.state_variables:
            editor = FloatEditor(self.model.states.get(state, 0))
            editor.valueChanged.connect(partial(self._edit_state, state))
            self.scrollLayout.addRow(
                BodyLabel(expression2unicode(state, False) + ":"), editor
            )
        # parameters
        self.scrollLayout.addWidget(SubtitleLabel("Parameter value:"))
        for parameter in dynamics.parameters:
            editor = FloatEditor(
                self.model.parameters.get(parameter, dynamics.parameters[parameter])
            )
            editor.valueChanged.connect(partial(self._edit_parameter, parameter))
            mylabel = BodyLabel(expression2unicode(parameter, False) + ":")
            mylabel.installEventFilter(
                ToolTipFilter(mylabel, 200, ToolTipPosition.LEFT)
            )
            if dynamics.docs:
                mylabel.setToolTip(dynamics.docs[parameter])
            self.scrollLayout.addRow(mylabel, editor)
        # stimulation
        self.stimulationPanel = StimulationPanel(self.model)
        self.scrollLayout.addRow(BodyLabel("stimulation:"), self.stimulationPanel)
        # solver
        self.scrollLayout.addWidget(SubtitleLabel("Simulation configuration:"))
        solver_editor = ModelSolverEditor(self.model)
        self.scrollLayout.addRow(BodyLabel("solver:"), solver_editor)
        # monitor
        monitors_editor: ListEditor[Monitor] = ListEditor(
            Raw,
            lambda: MonitorEditor(listen_attrs=True),
            self.model.monitors,
            listen_items=True,
        )
        monitors_editor.valueChanged.connect(partial(setattr, self.model, "monitors"))
        self.scrollLayout.addRow(BodyLabel("monitors:"), monitors_editor)
        # t
        t_editor = FloatEditor(self.model.t)
        t_editor.valueChanged.connect(partial(setattr, self.model, "t"))
        self.scrollLayout.addRow(BodyLabel("simulation time:"), t_editor)

    def _edit_state(self, name: str, value):
        self.model.states |= {name: value}

    def _edit_parameter(self, name: str, value):
        self.model.parameters |= {name: value}

    def _stimulation_dialog(self):
        w = StimulationDialog("Add Stimulation", self.model.atlas, self.model, self)
        w.exec()
        _getdata = None
        if w.getflag() == "ok":
            _getdata = w.getData()
            _stimulus_data = _getdata["valuelist"]
            for _, v in _stimulus_data.items():
                if v == None or v == "":
                    show_error("Add failed due to missing parameters", self)
                    return
            if _getdata["type"] == "Gaussian":
                _stimulation = GaussianStimulus(
                    amp=_stimulus_data["amp"],
                    mu=_stimulus_data["mu"],
                    sigma=_stimulus_data["sigma"],
                    offset=_stimulus_data["offset"],
                    space=_stimulus_data["space"],
                )
            elif _getdata["type"] == "NCyclePulse":
                _stimulation = NCyclePulseStimulus(
                    amp=_stimulus_data["amp"],
                    start=_stimulus_data["start"],
                    width=_stimulus_data["width"],
                    period=_stimulus_data["period"],
                    count=_stimulus_data["count"],
                    space=_stimulus_data["space"],
                )
            elif _getdata["type"] == "Pulse":
                _stimulation = PulseStimulus(
                    amp=_stimulus_data["amp"],
                    start=_stimulus_data["start"],
                    width=_stimulus_data["width"],
                    space=_stimulus_data["space"],
                )
            elif _getdata["type"] == "Sinusoid":
                _stimulation = SinusoidStimulus(
                    amp=_stimulus_data["amp"],
                    freq=_stimulus_data["freq"],
                    phase=_stimulus_data["phase"],
                    offset=_stimulus_data["offset"],
                    space=_stimulus_data["space"],
                )
            self.addStimulationToModel(_getdata["param"], _stimulation)
            self.stimulationPanel.addStimulationToPanel(_getdata["param"], _stimulation)

    def addStimulationToModel(self, param, stimulation):
        """将刺激添加到 DTB Model 中

        Parameters
        ----------
        param : str
            添加刺激的参数名称
        stimulation : GaussianStimulus | NCyclePulseStimulus | PulseStimulus | SinusoidStimulus
            一个刺激的实例
        """
        _temp = self.model.parameters
        _temp.update({param: stimulation})
        self.model.parameters = _temp


class InputWidget(QWidget):
    """添加刺激空间分布的条目"""

    deleteItemSignal = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inputBox = LineEdit(self)
        self._inputBox.setDisabled(True)
        self._inputBox.setMinimumWidth(200)
        self._btn = TransparentToolButton(FluentIcon.DELETE)
        self._btn.clicked.connect(self.deleteItem)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self._inputBox)
        self.layout.addWidget(self._btn)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def setText(self, text):
        self._inputBox.setText(text)

    def deleteItem(self):
        self.deleteItemSignal.emit(self)


class StimulationPanel(QWidget):
    """刺激板块"""

    def __init__(self, model: DTBModel, parent=None):
        super().__init__(parent)
        self._model = model
        self.formLayout = QFormLayout(self)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        for k, v in self._model.parameters.items():
            self.addStimulationToPanel(k, v)

    def addStimulationToPanel(self, param, stimulation):
        """将刺激添加到面板中

        Parameters
        ----------
        param : str
            添加刺激的参数名称
        stimulation : GaussianStimulus | NCyclePulseStimulus | PulseStimulus | SinusoidStimulus
            一个刺激的实例
        """
        _text = ""
        if isinstance(stimulation, GaussianStimulus):
            _text = str(
                f"GaussianStimulus: amp = {stimulation.amp},mu={stimulation.mu},sigma={stimulation.sigma},offset={stimulation.offset},space=<list>"
            )
        elif isinstance(stimulation, NCyclePulseStimulus):
            _text = str(
                f"NCyclePulseStimulus: amp = {stimulation.amp},start={stimulation.start},width={stimulation.width},period={stimulation.period},count={stimulation.count},space=<list>"
            )
        elif isinstance(stimulation, PulseStimulus):
            _text = str(
                f"PulseStimulus: amp = {stimulation.amp},start={stimulation.start},width={stimulation.width},space=<list>"
            )
        elif isinstance(stimulation, SinusoidStimulus):
            _text = str(
                f"SinusoidStimulus: amp = {stimulation.amp},freq={stimulation.freq},phase={stimulation.phase},offset={stimulation.offset},space=<list>"
            )
        else:
            _text = f"{stimulation.__class__.__name__}:{str(stimulation)}"
        # 判断是否已经有对应参数的刺激
        index = -1
        for i in range(self.formLayout.count()):
            if isinstance(
                self.formLayout.itemAt(i).widget(), BodyLabel
            ) and self.formLayout.itemAt(i).widget().text().replace(
                ":", ""
            ) == expression2unicode(
                param
            ):
                index = i
                break
        if not index == -1:
            self.formLayout.itemAt(i + 1).widget().setText(_text)
        else:
            cont = InputWidget(self)
            cont.deleteItemSignal.connect(self.deleteStimulation)
            cont.setText(_text)
            mylabel = BodyLabel(expression2unicode(param, False) + ":")
            self.formLayout.addRow(mylabel, cont)

    def deleteStimulation(self, widget: InputWidget):
        """删除一个刺激条目

        Parameters
        ----------
        widget : InputWidget
            不包含label的一个 widget
        """
        index = 0
        for i in range(self.formLayout.count()):
            if self.formLayout.itemAt(i).widget() == widget:
                index = i
                break
        _label = self.formLayout.itemAt(index - 1).widget()
        _param_name = _label.text().replace(":", "")
        _editor = self.formLayout.itemAt(index).widget()
        self.formLayout.removeWidget(_label)
        self.formLayout.removeWidget(_editor)
        _label.deleteLater()
        _editor.deleteLater()
        # 删除模型中对应的刺激
        _stimulation = self._model.parameters
        for k, _ in _stimulation.items():
            if expression2unicode(k) == expression2unicode(_param_name):
                _key = k
                break
        del _stimulation[_key]
        self._model.parameters = _stimulation


class ModelSolverEditor(InstanceEditor[Solver]):
    def __init__(self, model: DTBModel, parent=None):
        self._model = model
        self._init_factories()
        super().__init__(model.solver, True, parent)

        self.valueChanged.connect(self._value_changed)

    def _value_changed(self, value):
        self._model.solver = value

    def _init_factories(self):
        self._public_attr_factories = [
            InstanceEditorAttr("dt", FloatEditor),
            InstanceEditorAttr("noises", self._noise_editor),
        ]

        self.factories = [
            InstanceEditorFactory[Solver].from_type(
                solver, self._public_attr_factories, name
            )
            for name, solver in SOLVER_DICT.items()
        ]

    def _noise_editor(self):
        keys = list(self._model.dynamics.state_variables)
        editor = KeySetDictEditor(
            keys,
            lambda _: 0,
            FloatEditor,
            key2str=partial(expression2unicode, rich=False),
            listen_items=True,
        )
        return editor


class MonitorEditor(InstanceEditor[Monitor]):
    factories = [
        InstanceEditorFactory[Monitor].from_type(
            Raw, [InstanceEditorAttr("expression", LineEditor)]
        ),
        InstanceEditorFactory[Monitor].from_type(
            SubSample,
            [
                InstanceEditorAttr("expression", LineEditor),
                InstanceEditorAttr("sample_interval", IntEditor),
            ],
        ),
        InstanceEditorFactory[Monitor].from_type(
            TemporalAverage,
            [
                InstanceEditorAttr("expression", LineEditor),
                InstanceEditorAttr("sample_interval", IntEditor),
            ],
        ),
        InstanceEditorFactory[Monitor].from_type(
            BOLD,
            [
                InstanceEditorAttr("expression", LineEditor),
                InstanceEditorAttr("sample_interval", IntEditor),
                InstanceEditorAttr("taus", FloatEditor),
                InstanceEditorAttr("tauf", FloatEditor),
                InstanceEditorAttr("tauo", FloatEditor),
                InstanceEditorAttr("alpha", FloatEditor),
                InstanceEditorAttr("Eo", FloatEditor),
                InstanceEditorAttr("TE", FloatEditor),
                InstanceEditorAttr("vo", FloatEditor),
            ],
        ),
    ]
