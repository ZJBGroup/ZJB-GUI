from PyQt5.QtWidgets import QWidget
from qfluentwidgets import BodyLabel, TransparentPushButton, PrimaryPushButton
from PyQt5.QtWidgets import QHBoxLayout
from .._global import GLOBAL_SIGNAL, get_workspace
from ..pages.analysis_page import AnalysisPage
from ..pages.connectivity_page import ConnectivityPage
from ..pages.surface_page import SurfacePage
from ..pages.time_series_page import RegionalTimeSeriesPage
from zjb.main.api import SimulationResult, Surface, Connectivity


class DataOperationPanel(QWidget):

    def __init__(self, name, data, subject=None, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DataManipulation")
        self.name = name
        self.data = data
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
        btn_visualization = TransparentPushButton('Visualization')
        btn_analysis = TransparentPushButton('Analysis')
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
                timeseries._gid.str + 'Visualization',
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

    def _click_analysis(self):
        if isinstance(self.data, SimulationResult):
            timeseries = self.data.data[0]
            self._workspace = get_workspace()

            GLOBAL_SIGNAL.requestAddPage.emit(
                timeseries._gid.str + 'Analysis',
                lambda _: AnalysisPage(timeseries),
            )

        elif isinstance(self.data, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self.data._gid.str + 'Analysis',
                lambda _: AnalysisPage(self.data),
            )

        elif isinstance(self.data, Connectivity):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self.data._gid.str + 'Analysis',
                lambda _: AnalysisPage(self.data),
            )








