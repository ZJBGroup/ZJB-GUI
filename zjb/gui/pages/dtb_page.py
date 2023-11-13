from functools import partial
from typing import Any

import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    LineEdit,
    MessageBoxBase,
    PrimaryPushButton,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
    TransparentPushButton,
)

from zjb.doj.job import GeneratorJob, Job, JobState
from zjb.main.api import DTB, PSEResult, SimulationResult
from zjb.main.dtb.utils import expression2unicode

from .._global import GLOBAL_SIGNAL, get_workspace
from ..common.utils import show_error, show_success
from ..panels.data_operation_panel import DataOperationPanel
from ..widgets.choose_data_dialog import ChooseDataDialog
from ..widgets.dict_editor import KeySetDictEditor
from ..widgets.editor import FloatEditor, LineEditor
from .base_page import BasePage
from .connectivity_page import ConnectivityPage
from .dtb_model_page import DTBModelPage
from .subject_page import SubjectPage


class DTBPage(BasePage):
    def __init__(self, dtb: DTB, project: Project):
        super().__init__(dtb._gid.str, dtb.name, FluentIcon.ALBUM)
        self.dtb = dtb
        self.project = project

        self._setup_ui()

        self._sync_data()
        self.currentPageSignal.connect(self._sync_data)

        self._running_jobs: dict[str, Job] = {}
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)
        self._timer.start(1000)

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.vBoxLayout.addWidget(TitleLabel("DTB"))
        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.addLayout(self.formLayout)

        self.formLayout.addRow(BodyLabel("name:"), BodyLabel(self.dtb.name))
        btn_subject = TransparentPushButton(self.dtb.subject.name)
        btn_subject.clicked.connect(self._click_subject)
        self.formLayout.addRow(BodyLabel("subject:"), btn_subject)

        btn_model = TransparentPushButton(self.dtb.model.name)
        btn_model.clicked.connect(self._click_model)
        self.formLayout.addRow(BodyLabel("model:"), btn_model)

        btn_connectivity = TransparentPushButton(f"{self.dtb.connectivity}")
        btn_connectivity.clicked.connect(self._click_connectivity)

        self.formLayout.addRow(BodyLabel("connectivity:"), btn_connectivity)

        btn_simulate = PrimaryPushButton(f"Simulate")
        btn_simulate.clicked.connect(self._simulate)
        self.vBoxLayout.addWidget(btn_simulate)

        btn_pse = PrimaryPushButton(f"PSE")
        btn_pse.clicked.connect(self._pse)
        self.vBoxLayout.addWidget(btn_pse)

        self.scrollArea = SmoothScrollArea(self)
        self.vBoxLayout.addWidget(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

    def _sync_data(self):
        for i in reversed(range(self.scrollLayout.rowCount())):
            self.scrollLayout.removeRow(i)

        def _create_data_button(name, data):
            btn_data = TransparentPushButton(f"{name}")
            btn_data.clicked.connect(lambda: self._show_data_dialog(name, data))
            self.scrollLayout.addRow(btn_data)

        for name, data in self.dtb.data.items():
            if isinstance(data, SimulationResult) or isinstance(data, PSEResult):
                _create_data_button(name, data)
            elif data is None:
                self.scrollLayout.addRow(TransparentPushButton(f"{name}(running)"))
            else:
                data_manipulation_panel = DataOperationPanel(name, data, self.project)
                self.scrollLayout.addRow(data_manipulation_panel)

    def _poll(self):
        _removing = []
        for name, job in self._running_jobs.items():
            if job.state == JobState.ERROR:
                show_error(f"An error occurred while running {name}.", self.window())
                _removing.append(name)
                continue
            if job.state == JobState.DONE:
                show_success(f"Successfully run {name}.", self.window())
                _removing.append(name)
                continue
        if _removing:
            self._sync_data()
        for name in _removing:
            self._running_jobs.pop(name)

    def _simulate(self):
        ws = get_workspace()
        assert ws
        dialog = SimulationDialog(self.dtb, self)
        if not dialog.exec():
            return
        store_key = dialog.name
        with self.dtb:
            data = self.dtb.data
            if not store_key:
                store_key = _generate_key(data, "simulation")
            self.dtb.data = data | {store_key: None}
        self.scrollLayout.addRow(TransparentPushButton(f"{store_key}(running)"))
        job = Job(DTB.simulate, self.dtb, store_key=store_key)
        if dialog.params:
            job.kwargs |= {"dynamic_parameters": dialog.params}
        ws.manager.bind(job)
        self._running_jobs[store_key] = job
        GLOBAL_SIGNAL.joblistChanged.emit()
        show_success(f"Simulation {store_key} started!", self.window())

    def _pse(self):
        ws = get_workspace()
        assert ws
        dialog = PSEDialog(self.dtb, self)
        if not dialog.exec():
            return
        store_key = dialog.name
        with self.dtb:
            data = self.dtb.data
            if not store_key:
                store_key = _generate_key(data, "pse")
            self.dtb.data = data | {store_key: None}
        self.scrollLayout.addRow(TransparentPushButton(f"{store_key}(running)"))
        job = GeneratorJob(DTB.pse, self.dtb, dialog.params, store_key=store_key)
        ws.manager.bind(job)
        self._running_jobs[store_key] = job
        GLOBAL_SIGNAL.joblistChanged.emit()
        show_success(f"PSE {store_key} started!", self.window())

    def _click_subject(self):
        subject = self.dtb.subject
        GLOBAL_SIGNAL.requestAddPage.emit(
            subject._gid.str, lambda _: SubjectPage(subject)
        )

    def _click_model(self):
        model = self.dtb.model
        GLOBAL_SIGNAL.requestAddPage.emit(model._gid.str, lambda _: DTBModelPage(model))

    def _click_connectivity(self):
        connectivity = self.dtb.connectivity

        GLOBAL_SIGNAL.requestAddPage.emit(
            connectivity._gid.str, lambda _: ConnectivityPage(connectivity)
        )

    def _show_data_dialog(self, name, data):
        title = f"Data in {name}"
        content = """Select data for visualization or analysis."""
        w = ChooseDataDialog(data, self.project, self)
        w.exec()


class SimulationDialog(MessageBoxBase):
    def __init__(self, dtb: DTB, parent=None):
        super().__init__(parent)

        self._dtb = dtb
        self._parameters = dtb.model.dynamics.parameters | dtb.model.parameters
        self._params = {}

        self._setup_ui()

        self.name_edit.setText(_generate_key(dtb.data, "simulation"))

    def _setup_ui(self):
        self.viewLayout.addWidget(SubtitleLabel(self.tr("Configure Simulation:")))

        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.viewLayout.addLayout(self.formLayout)

        self.name_edit = LineEdit()
        self.name_edit.setPlaceholderText("Input a name here")
        self.formLayout.addRow(BodyLabel("name:"), self.name_edit)

        self.scrollLayout = SmoothScrollArea()
        self.scrollLayout.setWidgetResizable(True)
        self.scrollLayout.setMinimumSize(300, 200)
        self.formLayout.addRow(BodyLabel("parameters:"), self.scrollLayout)

        self.params_editors = KeySetDictEditor(
            self._parameters,
            lambda key: self._parameters[key],
            FloatEditor,
            self._params,
            key2str=partial(expression2unicode, rich=False),
            listen_items=True,
            dialog_parent=self.parent(),
        )
        self.scrollLayout.setWidget(self.params_editors)

    @property
    def params(self):
        return self._params

    @property
    def name(self):
        return self.name_edit.text()


class PSEDialog(MessageBoxBase):
    def __init__(self, dtb: DTB, parent=None):
        super().__init__(parent)

        self._dtb = dtb
        self._parameters = dtb.model.dynamics.parameters | dtb.model.parameters
        self._params = {}

        self._setup_ui()

        self.name_edit.setText(_generate_key(dtb.data, "pse"))

    def _setup_ui(self):
        self.viewLayout.addWidget(SubtitleLabel(self.tr("Configure PSE:")))

        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.viewLayout.addLayout(self.formLayout)

        self.name_edit = LineEdit()
        self.name_edit.setPlaceholderText("Input a name here")
        self.formLayout.addRow(BodyLabel("name:"), self.name_edit)

        self.scrollLayout = SmoothScrollArea()
        self.scrollLayout.setWidgetResizable(True)
        self.scrollLayout.setMinimumSize(280, 180)
        self.formLayout.addRow(BodyLabel("parameters:"), self.scrollLayout)

        self.params_editors = KeySetDictEditor(
            self._parameters,
            lambda key: [self._parameters[key]],
            partial(LineEditor, _to=self._str2list),
            self._params,
            key2str=partial(expression2unicode, rich=False),
            listen_items=True,
            dialog_parent=self.parent(),
        )
        self.params_editors.valueChanged.connect(self._ps_changed)
        self.scrollLayout.setWidget(self.params_editors)

        self.stat_label = BodyLabel("0 parameters will be simulated")
        self.viewLayout.addWidget(self.stat_label)

    @property
    def params(self):
        return self._params

    @property
    def name(self):
        return self.name_edit.text()

    def _str2list(self, _str: str):
        return list(eval(_str, {"linspace": np.linspace, "arange": np.arange}))

    def _ps_changed(self, _):
        sizes = [str(len(para)) for para in self._params.values()]
        self.stat_label.setText(f"{'×'.join(sizes)} parameters will be simulated")


def _generate_key(_dict: dict[str, Any], prefix: str):
    pattern = re.compile(rf"{prefix}-(\d+)")
    _max = 0
    for name in _dict:
        if res := pattern.fullmatch(name):
            value = int(res.groups()[0])
            if value > _max:
                _max = value
    _max += 1
    return f"{prefix}-{_max}"
