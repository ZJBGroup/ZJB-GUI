from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    IconWidget,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
    ToolTipFilter,
    ToolTipPosition,
    TransparentPushButton,
)
from zjb.main.api import (
    BOLD,
    SOLVER_DICT,
    DTBModel,
    Monitor,
    Raw,
    Solver,
    SubSample,
    TemporalAverage,
)
from zjb.main.dtb.utils import expression2unicode

from .._global import GLOBAL_SIGNAL, get_workspace
from ..widgets.dict_editor import KeySetDictEditor
from ..widgets.editor import FloatEditor, IntEditor, LineEditor
from ..widgets.instance_editor import (
    InstanceEditor,
    InstanceEditorAttr,
    InstanceEditorFactory,
)
from ..widgets.list_editor import ListEditor
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
        self.scrollLayout.addWidget(SubtitleLabel("Simulation configuration:"))
        # solver
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
