from PyQt5.QtCore import Qt
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
from zjb.main.api import (
    DTB,
    Connectivity,
    DTBModel,
    Project,
    PSEResult,
    SimulationResult,
    Subject,
    Surface,
    Workspace,
)

from .._global import GLOBAL_SIGNAL, get_workspace
from ..pages.analysis_page import AnalysisPage
from ..pages.connectivity_page import ConnectivityPage
from ..pages.surface_page import SurfacePage
from ..pages.time_series_page import RegionalTimeSeriesPage
from ..widgets.choose_data_dialog import ChooseDataDialog


def format_file_name(filename, length):
    """文件名长度超过 length 时 将多余的部分转换成省略号

    Parameters:
    ----------
    filename: str
        文件名
    length: num
        需要限制的长度
    """
    namestr = filename
    flag = False
    while len(namestr.encode("utf-8")) > length:
        namestr = namestr[: len(namestr) - 1]
        flag = True

    if flag:
        namestr = f"{namestr}..."

    return namestr


class Fileitem(CardWidget):
    def __init__(self, text: str, data, subject, project, parent=None):
        """数据列表中的一个数据文件基类"""
        super().__init__(parent)
        self._text = text
        self._data = data
        self._subject = subject
        self._project = project
        self._parent = parent
        self.setFixedSize(140, 150)

        self.vlayout = QVBoxLayout(self)
        self.vlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fileicon = IconWidget(FluentIcon.SYNC, self)
        self.fileicon.setFixedSize(100, 100)
        namestr = format_file_name(self._text, 16)
        self.filelabel = BodyLabel(namestr)
        self.filelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip(self._text)
        self.vlayout.addWidget(self.fileicon, 0, Qt.AlignmentFlag.AlignHCenter)
        self.vlayout.addWidget(self.filelabel, 1, Qt.AlignmentFlag.AlignHCenter)

    def _normalBackgroundColor(self):
        return QColor(255, 255, 255, 0)


class DTBFileitem(Fileitem):
    """DTB页面数据条目"""

    def __init__(self, text: str, data, subject, project, parent=None):
        super().__init__(text, data, subject, project, parent)

        if isinstance(self._data, SimulationResult):
            self.fileicon.setIcon(FluentIcon.DOCUMENT)

        if isinstance(self._data, PSEResult):
            self.fileicon.setIcon(FluentIcon.DICTIONARY)

        if not data == None:
            self.clicked.connect(lambda: self._show_data_dialog(self._text, self._data))
        else:
            self.filelabel.setText(f"{self._text}(running)")
            self.setToolTip(f"{self._text}(running)")

    def _show_data_dialog(self, name, data):
        """点击一个 dtb 模拟数据时，显示弹窗"""
        title = f"Data in {name}"
        content = """Select data for visualization or analysis."""
        w = ChooseDataDialog(data, self._project, self._parent)
        w.exec()


class SubjectFileitem(Fileitem):
    """subject页面数据条目"""

    def __init__(self, text: str, data, subject, project, parent=None):
        super().__init__(text, data, subject, project, parent)

        self.fileicon.setIcon(FluentIcon.BOOK_SHELF)
        if not data is None:
            if (
                isinstance(self._data, SimulationResult)
                or isinstance(self._data, Surface)
                or isinstance(self._data, Connectivity)
            ):
                self.clicked.connect(self._show_context_menu)

    def _show_context_menu(self):
        """点击一个 subject 数据条目时，触发右键菜单"""
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
                lambda _: RegionalTimeSeriesPage(timeseries, self._subject),
            )

        elif isinstance(self._data, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self._data._gid.str,
                lambda _: SurfacePage(self._data, f"{self._subject.name}-{self._text}"),
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
                lambda _: AnalysisPage(timeseries, self._project),
            )

        elif isinstance(self._data, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self._data._gid.str + "Analysis",
                lambda _: AnalysisPage(self._data, self._project),
            )

        elif isinstance(self._data, Connectivity):
            GLOBAL_SIGNAL.requestAddPage.emit(
                self._data._gid.str + "Analysis",
                lambda _: AnalysisPage(self._data, self._project),
            )


class DataListPanel(SmoothScrollArea):
    def __init__(
        self,
        text: str,
        data,
        subject: Subject,
        project: Project,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName(text.replace(" ", "_"))
        self._text = text
        self._data = data
        self._subject = subject
        self._project = project
        self._parent = parent

        # 数据文件 布局
        self.data_layout = FlowLayout(needAni=False)
        self.data_layout.setContentsMargins(0, 10, 0, 0)
        self.data_layout.setVerticalSpacing(10)
        self.data_layout.setHorizontalSpacing(10)

        # 滚动布局相关
        self.data_layout_container = QWidget()
        self.data_layout_container.setLayout(self.data_layout)
        self.container = QWidget(self)
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.addWidget(self.data_layout_container)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        if self._text == "subject":
            for name, data in self._data:
                print("value.class", data.__class__)
                self.data_layout.addWidget(
                    SubjectFileitem(
                        name, data, self._subject, self._project, self._parent
                    )
                )
        elif self._text == "dtb":
            for name, data in self._data:
                print("value.class", data.__class__)
                self.data_layout.addWidget(
                    DTBFileitem(name, data, self._subject, self._project, self._parent)
                )

        self.data_layout.setGeometry(self.data_layout.geometry())

    def sync_list(self, newdata):
        """有数据变化的时候更新整个区域"""
        self.data_layout.takeAllWidgets()
        if self._text == "subject":
            for key, value in newdata.items():
                self.data_layout.addWidget(
                    SubjectFileitem(
                        key,
                        value,
                        self._subject,
                        self._project,
                        self._parent,
                    )
                )
        elif self._text == "dtb":
            for key, value in newdata.items():
                self.data_layout.addWidget(
                    DTBFileitem(
                        key,
                        value,
                        self._subject,
                        self._project,
                        self._parent,
                    )
                )
        self.data_layout.setGeometry(self.data_layout.geometry())
