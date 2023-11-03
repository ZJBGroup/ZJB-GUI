from functools import partial

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    LineEdit,
    MessageBoxBase,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
    TransparentPushButton,
)

from zjb.doj.job import GeneratorJob, Job
from zjb.main.api import DTB, SimulationResult
from zjb.main.dtb.utils import expression2unicode

from .._global import GLOBAL_SIGNAL, get_workspace
from ..common.utils import show_success
from ..panels.data_operation_panel import DataOperationPanel
from ..widgets.dict_editor import KeySetDictEditor
from ..widgets.editor import LineEditor
from .base_page import BasePage
from .connectivity_page import ConnectivityPage
from .dtb_model_page import DTBModelPage
from .subject_page import SubjectPage


class DTBPage(BasePage):
    def __init__(self, dtb: DTB):
        super().__init__(dtb._gid.str, dtb.name, FluentIcon.ALBUM)
        self.dtb = dtb

        self._setup_ui()

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

        btn_simulate = TransparentPushButton(f"Simulate")
        btn_simulate.clicked.connect(self._simulate)
        self.vBoxLayout.addWidget(btn_simulate)

        btn_pse = TransparentPushButton(f"PSE")
        btn_pse.clicked.connect(self._pse)
        self.vBoxLayout.addWidget(btn_pse)

        self.scrollArea = SmoothScrollArea(self)
        self.vBoxLayout.addWidget(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        for name, data in self.dtb.data.items():
            data_manipulation_panel = DataOperationPanel(name, data)
            self.scrollLayout.addRow(data_manipulation_panel)

    def _simulate(self):
        job = Job(DTB.simulate, self.dtb)
        job.kwargs = {"store_key": job._gid.str}
        ws = get_workspace()
        assert ws
        ws.manager.bind(job)
        GLOBAL_SIGNAL.joblistChanged.emit()
        show_success(f"Simulation {job._gid.str} started!", self.window())

    def _pse(self):
        dialog = PSEDialog(self.dtb, self)
        if not dialog.exec():
            return
        job = GeneratorJob(DTB.pse, self.dtb, dialog.params, store_key=dialog.name)
        job.kwargs = {"store_key": dialog.name or ("PSE_" + job._gid.str)}
        ws = get_workspace()
        assert ws
        ws.manager.bind(job)
        GLOBAL_SIGNAL.joblistChanged.emit()
        show_success(f"PSE {job._gid.str} started!", self.window())

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


class PSEDialog(MessageBoxBase):
    def __init__(self, dtb: DTB, parent=None):
        super().__init__(parent)

        self._dtb = dtb
        self._parameters = dtb.model.dynamics.parameters | dtb.model.parameters
        self._params = {}

        self._setup_ui()

    def _setup_ui(self):
        self.viewLayout.addWidget(SubtitleLabel(self.tr("Configure PSE:")))

        self.name_edit = LineEdit()
        self.name_edit.setPlaceholderText("Input a name here")

        self.viewLayout.addWidget(self.name_edit)

        self.scrollLayout = SmoothScrollArea()
        self.scrollLayout.setWidgetResizable(True)
        self.scrollLayout.setMinimumSize(300, 200)
        self.viewLayout.addWidget(self.scrollLayout)

        self.params_editors = KeySetDictEditor(
            self._parameters,
            lambda key: [self._parameters[key]],
            partial(LineEditor, _to=self._str2list, _from=self._list2str),
            self._params,
            key2str=partial(expression2unicode, rich=False),
            can_add=True,
            can_remove=True,
            dialog_parent=self.parent(),
        )
        self.params_editors.itemAdded.connect(self._ps_changed)
        self.params_editors.itemChanged.connect(self._ps_changed)
        self.params_editors.itemRemoved.connect(self._ps_changed)
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

    def _list2str(self, _list):
        return ",".join(map(str, _list))

    def _ps_changed(self, key, value):
        sizes = [str(len(para)) for para in self._params.values()]
        self.stat_label.setText(f"{'×'.join(sizes)} parameters will be simulated")
