from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QPushButton, QVBoxLayout
from qfluentwidgets import BodyLabel, FluentIcon, TitleLabel, TransparentPushButton

from zjb.main.api import (
    Connectivity,
    RegionalTimeSeries,
    SpaceCorrelation,
    Subject,
    Surface,
)

from .._global import GLOBAL_SIGNAL
from ..panels.data_operation_panel import DataOperationPanel
from .base_page import BasePage
from .connectivity_page import ConnectivityPage
from .surface_page import SurfacePage
from .time_series_page import RegionalTimeSeriesPage


class SubjectPage(BasePage):
    def __init__(self, subject: Subject):
        super().__init__(subject._gid.str, subject.name, FluentIcon.PEOPLE)
        self.subject = subject

        self._setup_ui()

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.vBoxLayout.addWidget(TitleLabel("Subject"))
        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.addLayout(self.formLayout)

        self.formLayout.addRow(BodyLabel("name:"), BodyLabel(self.subject.name))
        self.formLayout.addRow(BodyLabel("info:"), BodyLabel("..."))

        for name, data in self.subject.data.items():
            data_manipulation_panel = DataOperationPanel(name, data)
            self.formLayout.addRow(data_manipulation_panel)
