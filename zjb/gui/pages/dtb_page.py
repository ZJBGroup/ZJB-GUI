from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    SmoothScrollArea,
    TitleLabel,
    TransparentPushButton,
)

from zjb.doj.job import Job
from zjb.main.api import DTB

from .._global import GLOBAL_SIGNAL, get_workspace
from ..common.utils import show_success
from .base_page import BasePage
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
        self.formLayout.addRow(BodyLabel("connectivity:"), btn_connectivity)

        btn_simulate = TransparentPushButton(f"Simulate")
        btn_simulate.clicked.connect(self._simulate)
        self.vBoxLayout.addWidget(btn_simulate)

        self.scrollArea = SmoothScrollArea(self)
        self.vBoxLayout.addWidget(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        for name, data in self.dtb.data.items():
            self.scrollLayout.addRow(BodyLabel(name + ":"), BodyLabel(f"{data}"))

    def _simulate(self):
        job = Job(func=DTB.simulate, args=(self.dtb,))
        job.kwargs = {"store_key": job._gid.str}
        get_workspace().manager.bind(job)
        show_success(f"Simulation {job._gid.str} started!", self.window())

    def _click_subject(self):
        subject = self.dtb.subject
        GLOBAL_SIGNAL.requestAddPage.emit(
            subject._gid.str, lambda _: SubjectPage(subject)
        )

    def _click_model(self):
        model = self.dtb.model
        GLOBAL_SIGNAL.requestAddPage.emit(model._gid.str, lambda _: DTBModelPage(model))
