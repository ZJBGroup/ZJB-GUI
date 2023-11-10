from PyQt5.QtCore import QEasingCurve, Qt
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import (
    Action,
    BodyLabel,
    CardWidget,
    FlowLayout,
    FluentIcon,
    IconWidget,
    RoundMenu,
    SmoothScrollArea,
)
from zjb.main.api import Connectivity, SimulationResult, Surface

from .._global import GLOBAL_SIGNAL, get_workspace
from ..pages.analysis_page import AnalysisPage
from ..pages.connectivity_page import ConnectivityPage
from ..pages.surface_page import SurfacePage
from ..pages.time_series_page import RegionalTimeSeriesPage


class Fileitem(CardWidget):
    def __init__(self, text: str, data, parent=None):
        super().__init__(parent)
        self._text = text
        self._data = data
        self.setFixedSize(140, 150)

        namestr = self._text
        flag = False
        while len(namestr.encode("utf-8")) > 16:
            namestr = namestr[: len(namestr) - 1]
            flag = True

        if flag:
            namestr = f"{namestr}..."

        self.setStyleSheet("*{border:none;}")
        self.vlayout = QVBoxLayout(self)
        self.vlayout.setAlignment(Qt.AlignCenter)
        self.fileicon = IconWidget(FluentIcon.DOCUMENT, self)
        self.fileicon.setFixedSize(100, 100)
        self.filelabel = BodyLabel(namestr)
        self.filelabel.setAlignment(Qt.AlignCenter)
        self.setToolTip(text)
        self.vlayout.addWidget(self.fileicon, 0, Qt.AlignHCenter)
        self.vlayout.addWidget(self.filelabel, 1, Qt.AlignHCenter)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _normalBackgroundColor(self):
        return QColor(255, 255, 255, 0)

    def _show_context_menu(self, _):
        """右键点击一个条目时，触发右键菜单"""
        menu = RoundMenu()
        self.visualization_action = Action(
            FluentIcon.DEVELOPER_TOOLS,
            "Visualization",
            triggered=self._click_visualization,
        )
        self.analysis_action = Action(
            FluentIcon.PIE_SINGLE,
            "Analysis",
            triggered=self._click_analysis,
        )
        menu.addAction(self.visualization_action)
        menu.addAction(self.analysis_action)

        menu.exec_(QCursor.pos())

    def _click_visualization(self):
        # TODO: 支持其他类型的数据
        if isinstance(self._data, SimulationResult):
            timeseries = self._data.data[0]
            self._workspace = get_workspace()

            GLOBAL_SIGNAL.requestAddPage.emit(
                timeseries._gid.str + "Visualization",
                lambda _: RegionalTimeSeriesPage(timeseries, self.subject),
            )

        elif isinstance(self._data, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self._data._gid.str,
                lambda _: SurfacePage(self._data, f"{self.subject.name}-{self.name}"),
            )

        elif isinstance(self._data, Connectivity):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self._data._gid.str,
                lambda _: ConnectivityPage(self._data),
            )

    def _click_analysis(self):
        if isinstance(self._data, SimulationResult):
            timeseries = self._data.data[0]
            self._workspace = get_workspace()

            GLOBAL_SIGNAL.requestAddPage.emit(
                timeseries._gid.str + "Analysis",
                lambda _: AnalysisPage(timeseries),
            )

        elif isinstance(self._data, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self._data._gid.str + "Analysis",
                lambda _: AnalysisPage(self._data),
            )

        elif isinstance(self._data, Connectivity):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self._data._gid.str + "Analysis",
                lambda _: AnalysisPage(self._data),
            )


class DataListPanel(SmoothScrollArea):
    def __init__(self, text: str, data, parent=None):
        super().__init__(parent)
        self.setObjectName(text.replace(" ", "_"))
        self._data = data

        # 数据文件 布局
        self.data_layout = FlowLayout(needAni=True)
        self.data_layout.setAnimation(250, QEasingCurve.OutQuad)
        self.data_layout.setContentsMargins(0, 10, 0, 0)
        self.data_layout.setVerticalSpacing(10)
        self.data_layout.setHorizontalSpacing(10)

        # 滚动布局相关
        self.data_layout_container = QWidget()
        self.data_layout_container.setLayout(self.data_layout)
        self.container = QWidget(self)
        # self.setStyleSheet("QWidget{background-color: transparent;border:none;}")
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.addWidget(self.data_layout_container)
        self.main_layout.setAlignment(Qt.AlignTop)

        for name, data in self._data:
            self.data_layout.addWidget(Fileitem(name, data))

        self.data_layout.setGeometry(self.data_layout.geometry())

    def sync_list(self, newdata):
        """有数据变化的时候更新整个区域"""
        self.data_layout.takeAllWidgets()
        for key, value in newdata.items():
            self.data_layout.addWidget(Fileitem(key, value))
