from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QPushButton, QVBoxLayout
from qfluentwidgets import BodyLabel, FluentIcon, TitleLabel, TransparentPushButton

from zjb.main.api import Subject, Surface, Connectivity, RegionalTimeSeries, SpaceCorrelation

from .connectivity_page import ConnectivityPage
from .time_series_page import RegionalTimeSeriesPage
from .._global import GLOBAL_SIGNAL
from .base_page import BasePage
from .surface_page import SurfacePage


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
            if isinstance(data, Surface):
                btn = TransparentPushButton(f"{data}")

                def add_page(data: Surface):
                    GLOBAL_SIGNAL.requestAddPage.emit(
                        data._gid.str,
                        lambda _: SurfacePage(data, f"{self.subject.name}-{name}"),
                    )

                btn.clicked.connect(partial(add_page, data))
                self.formLayout.addRow(BodyLabel(name + ":"), btn)
                continue

            if isinstance(data, Connectivity):
                btn = TransparentPushButton(f"{data}")

                def add_page(data: Connectivity):
                    GLOBAL_SIGNAL.requestAddPage.emit(
                        data._gid.str,
                        lambda _: ConnectivityPage(data),
                    )

                btn.clicked.connect(partial(add_page, data))
                self.formLayout.addRow(BodyLabel(name + ":"), btn)
                continue

            if isinstance(data, RegionalTimeSeries):
                btn = TransparentPushButton(f"{data}")

                def add_page(data: RegionalTimeSeries):
                    GLOBAL_SIGNAL.requestAddPage.emit(
                        data._gid.str,
                        lambda _: RegionalTimeSeriesPage(data, self.subject),
                    )

                btn.clicked.connect(partial(add_page, data))
                self.formLayout.addRow(BodyLabel(name + ":"), btn)
                continue

            self.formLayout.addRow(BodyLabel(name + ":"), BodyLabel(f"{data}"))
