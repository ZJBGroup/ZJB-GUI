from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    MessageBoxBase,
    SmoothScrollArea,
    TitleLabel,
    TransparentPushButton,
)

from zjb.main.api import (
    AnalysisResult,
    Connectivity,
    RegionalTimeSeries,
    SimulationResult,
    Surface,
)
from .._global import GLOBAL_SIGNAL, get_workspace
from ..pages.analysis_page import AnalysisPage
from ..pages.connectivity_page import ConnectivityPage
from ..pages.surface_page import SurfacePage
from ..pages.time_series_page import RegionalTimeSeriesPage


class DataOperationPanel(QWidget):
    def __init__(self, name, data, project, subject=None, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DataManipulation")
        self.name = name
        self.data = data
        self.project = project

        self._workspace = get_workspace()
        self._default_subject(subject)

        self._setup_ui()

    def _default_subject(self, subject):
        if not subject:
            for subject_ws in self._workspace.subjects:
                if subject_ws.name == "fsaverage":
                    self.subject = subject_ws
                    break
        else:
            self.subject = subject

    def _setup_ui(self):
        self.hBoxLayout = QHBoxLayout(self)
        btn_visualization = TransparentPushButton("Visualization")
        btn_analysis = TransparentPushButton("Analysis")
        btn_visualization.clicked.connect(self._click_visualization)
        btn_analysis.clicked.connect(self._click_analysis)

        self.hBoxLayout.addWidget(BodyLabel(self.name + ":"))
        self.hBoxLayout.addWidget(btn_visualization)
        self.hBoxLayout.addWidget(btn_analysis)

    def _click_visualization(self):
        # TODO: 支持其他类型的数据
        if isinstance(self.data, SimulationResult):
            timeseries = self.data.data[0]
            self._workspace = get_workspace()

            GLOBAL_SIGNAL.requestAddPage.emit(
                timeseries._gid.str + "Visualization",
                lambda _: RegionalTimeSeriesPage(timeseries, self.subject),
            )

        elif isinstance(self.data, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self.data._gid.str,
                lambda _: SurfacePage(self.data, f"{self.subject.name}-{self.name}"),
            )

        elif isinstance(self.data, Connectivity):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self.data._gid.str,
                lambda _: ConnectivityPage(self.data),
            )

        elif isinstance(self.data, RegionalTimeSeries):
            if self.data.space.atlas.name == "AAL90":
                for subject in self._workspace.subjects:
                    if subject.name == "cortex_80k":
                        self.subject = subject

            GLOBAL_SIGNAL.requestAddPage.emit(
                self.data._gid.str,
                lambda _: RegionalTimeSeriesPage(self.data, self.subject),
            )

    def _click_analysis(self):
        dialog = ChooseAnalysisDialog(
            self.data, self.project, self.parent().parent().parent().parent().parent()
        )
        dialog.exec()


class ChooseAnalysisDialog(MessageBoxBase):
    def __init__(self, data, project, parent=None):
        super().__init__(parent)
        self.data = data
        self.project = project
        self._setup_ui()

    def _setup_ui(self):
        self.yesButton.setText("Close")
        self.cancelButton.hide()
        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.formLayout.addRow(TitleLabel("Existing Analysis:"))

        self.scrollArea = SmoothScrollArea(self)

        self.formLayout.addRow(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)

        self.scrollWidget = QWidget(self.scrollArea)

        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # 查找项目中现有关联该数据的分析
        for data in self.project.data:
            if isinstance(data, AnalysisResult) and self.data in data.origin:
                btn_existe = self._create_data_button(data.name, data)
                self.scrollLayout.addRow(btn_existe)

        for dtb in self.project.available_dtbs():
            for key, value in dtb.data.items():
                if isinstance(value, AnalysisResult) and self.data in value.origin:
                    btn_existe = self._create_data_button(key, value)
                    self.scrollLayout.addRow(btn_existe)

        for subject in self.project.available_subjects():
            for key, value in subject.data.items():
                if isinstance(value, AnalysisResult) and self.data in value.origin:
                    btn_existe = self._create_data_button(key, value)
                    self.scrollLayout.addRow(btn_existe)

        btn_add_new_analysis = TransparentPushButton("New Analysis")
        btn_add_new_analysis.clicked.connect(self._click_new_analysis)

        self.formLayout.addRow(btn_add_new_analysis)

        self.viewLayout.addLayout(self.formLayout)

    def _create_data_button(self, name, data):
        btn_data = TransparentPushButton(f"{name}")
        btn_data.clicked.connect(lambda: self._show_exist_analysis(name, data))
        return btn_data

    def _click_new_analysis(self):
        if isinstance(self.data, SimulationResult):
            timeseries = self.data.data[0]
            self._workspace = get_workspace()

            GLOBAL_SIGNAL.requestAddPage.emit(
                timeseries._gid.str + "Analysis",
                lambda _: AnalysisPage(timeseries, self.project),
            )

        elif isinstance(self.data, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self.data._gid.str + "Analysis",
                lambda _: AnalysisPage(self.data, self.project),
            )

        elif isinstance(self.data, Connectivity):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self.data._gid.str + "Analysis",
                lambda _: AnalysisPage(self.data, self.project),
            )

        elif isinstance(self.data, RegionalTimeSeries):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self.data._gid.str + "Analysis",
                lambda _: AnalysisPage(self.data, self.project),
            )

    def _show_exist_analysis(self, name, data):
        if isinstance(data, AnalysisResult):
            GLOBAL_SIGNAL.requestAddPage.emit(
                data._gid.str + "Analysis",
                lambda _: AnalysisPage(data, self.project),
            )
