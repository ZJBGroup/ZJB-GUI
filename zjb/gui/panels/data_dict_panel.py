from functools import partial
from typing import TYPE_CHECKING, Any

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

from zjb.dos import Data
from zjb.main.api import (
    DTB,
    Connectivity,
    Project,
    PSEResult,
    RegionalTimeSeries,
    SimulationResult,
    Subject,
    Surface,
)
from zjb.main.data.series import MNEsimSeries
from .._global import GLOBAL_SIGNAL, get_workspace
from ..common.utils import show_success
from ..pages.analysis_page import AnalysisPage
from ..pages.connectivity_page import ConnectivityPage
from ..pages.mne_page import RawArrayPage
from ..pages.surface_page import SurfacePage
from ..pages.time_series_page import RegionalTimeSeriesPage
from ..widgets.choose_data_dialog import ChooseDataDialog
from ..widgets.extract_data_dialog import PSEDataDialog, SimulationResultDialog

if TYPE_CHECKING:
    from ..pages.dtb_page import DTBPage
    from ..pages.subject_page import SubjectPage


class DataDictPanel(SmoothScrollArea):
    """数据字典面板, 用于展示和操作以字典形式存储的数据

    Attributes
    ----------
    data: dict[str, Any]
        面板对应的数据字典, 字典内部发生变化时需要调用:py:method:`notify_data_changed`更新面板
        直接赋值:py:attr:`data`变更整个数据字典时, 会自动更新面板
    """

    def __init__(self, data: dict[str, Any], parent=None):
        super().__init__(parent)

        self._setup_ui()

        self.data = data

    def _setup_ui(self):
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

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: dict[str, Any]):
        self._data = data
        self.notify_data_changed()

    def notify_data_changed(self):
        """通知数据发生变化
        由于字典是可变对象, 在字典变化需要调用此方法更新控件
        """
        self.data_layout.takeAllWidgets()

        for key, value in self._data.items():
            self.data_layout.addWidget(self._widget_for_item(key, value))

        self.data_layout.setGeometry(self.data_layout.geometry())

    def _widget_for_item(self, name: str, item: Any):
        """根据数据项目创建控件"""
        return DataItem(name, item, FluentIcon.SYNC, self)


class DataItem(CardWidget):
    """数据字典面板中的数据项目控件
    Parameters
    ----------
    name: str
        项目名
    item: Any
        项目对象
    icon: QIcon
        项目图标
    parent: DataDictPanel
        项目所在的数据字典面板
    """

    def __init__(
        self, name: str, item: Any, icon: "FluentIcon | str", parent: "DataDictPanel"
    ):
        super().__init__(parent)
        self._item = item
        self._name = name

        self._setup_ui()

        self.filelabel.setText(format_name(self._name))
        self.fileicon.setIcon(icon)

    def _setup_ui(self):
        self.vlayout = QVBoxLayout(self)
        self.vlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fileicon = IconWidget(self)
        self.fileicon.setFixedSize(100, 100)
        self.filelabel = BodyLabel()
        self.filelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip(self._name)
        self.vlayout.addWidget(self.fileicon, 0, Qt.AlignmentFlag.AlignHCenter)
        self.vlayout.addWidget(self.filelabel, 1, Qt.AlignmentFlag.AlignHCenter)

    @property
    def item(self):
        return self._item

    @property
    def name(self):
        return self._name

    def _normalBackgroundColor(self):
        return QColor(255, 255, 255, 0)


def format_name(name: str, max_length: int = 16):
    """将名称字符串中长度超过`max_length`的部分转换成省略号

    Parameters:
    ----------
    name: str
        要格式化的字符串
    length: int
        需要限制的长度, by default 16
    """
    if len(name) > max_length:
        name = name[: len(name) - 1]
        name = f"{name}..."

    return name


class DTBDataDictPanel(DataDictPanel):
    """DTB数据字典面板"""

    def __init__(self, dtb: DTB, project: Project, parent: "DTBPage"):
        super().__init__(dtb.data, parent)
        self._dtb = dtb
        self._project = project
        self._page = parent

    def _show_data_dialog(
        self, name: str, item: "SimulationResult | PSEResult | MNEsimSeries"
    ):
        # 在Panel中启动对话框可以避免Item被销毁可能导致的问题
        # dialog = ChooseDataDialog(item, self._project, self._page)

        _getdata = item
        if isinstance(_getdata, PSEResult):
            pse_data_dialog = PSEDataDialog(item, "PSE data", self._page)
            pse_data_dialog.cancelButton.setText("Delete")
            pse_data_dialog.rejected.connect(partial(self._delete_item, name, item))
            pse_data_dialog.exec()
            if pse_data_dialog.getflag() == "canel":
                _getdata = "canel"
            else:
                _getdata = pse_data_dialog.get_data()

            if _getdata == "canel":
                return

        if isinstance(_getdata, SimulationResult):
            simulation_result_dialog = SimulationResultDialog(
                _getdata, "Simulation data", self._dtb, self
            )
            simulation_result_dialog.cancelButton.setText("Delete")

            simulation_result_dialog.rejected.connect(
                partial(self._delete_item, name, item)
            )
            simulation_result_dialog.exec()

            if simulation_result_dialog.getflag() == "canel":
                _getdata = "canel"
            else:
                _getdata = simulation_result_dialog.get_timeseries_data()
        else:
            return

        if isinstance(_getdata, RegionalTimeSeries):
            dialog = ChooseDataDialog(_getdata, self._project, self._page)
            dialog.rejected.connect(partial(self._delete_item, name, item))
            dialog.show()

    def _delete_item(self, name: str, item: Any):
        """删除数据字典中的项目

        Parameters
        ----------
        name : str
            项目名（键）
        item : Any
            项目值
        """
        # 从数据字典中移除
        del self._data[name]
        self._dtb.data = self._data
        if isinstance(item, Data):
            # 如果项目本身是Data则从数据管理器中移除
            item.unbind()
        self.notify_data_changed()
        show_success(f"{name} deleted!", self.window())

    def _widget_for_item(self, name: str, item: Any):
        if item is None:
            return super()._widget_for_item(name + "(running)", item)
        if isinstance(item, SimulationResult):
            widget = DataItem(name, item, FluentIcon.DOCUMENT, self)
            widget.clicked.connect(partial(self._show_data_dialog, name, item))
            return widget
        if isinstance(item, PSEResult):
            widget = DataItem(name, item, FluentIcon.DICTIONARY, self)
            widget.clicked.connect(partial(self._show_data_dialog, name, item))
            return widget
        if isinstance(item, MNEsimSeries):
            widget = DataItem(name, item, FluentIcon.DOCUMENT, self)
            widget.clicked.connect(lambda: self._clicked_mne(item))
            return widget
        return super()._widget_for_item(name, item)

    def _clicked_mne(self, item):
        GLOBAL_SIGNAL.requestAddPage.emit(item._gid.str, lambda _: RawArrayPage(item))


class SubjectDataDictPanel(DataDictPanel):
    """被试数据字典面板"""

    def __init__(self, subject: Subject, project: Project, parent: "SubjectPage"):
        super().__init__(subject.data, parent)

        self._subject = subject
        self._project = project
        self._page = parent

    def _show_context_menu(self, widget: DataItem):
        """点击一个`subject`数据条目时，触发右键菜单"""
        menu = RoundMenu()
        visualization_action = Action(
            FluentIcon.DEVELOPER_TOOLS,
            "Visualization",
            triggered=partial(self._click_visualization, widget.name, widget.item),
        )
        analysis_action = Action(
            FluentIcon.PIE_SINGLE,
            "Analysis",
            triggered=partial(self._click_analysis, widget.item),
        )
        menu.addAction(visualization_action)
        menu.addAction(analysis_action)

        menu.exec_(QCursor.pos())

    def _click_visualization(self, name: str, item: Any):
        # TODO: 支持其他类型的数据
        if isinstance(item, SimulationResult):
            timeseries = item.data[0]
            self._workspace = get_workspace()

            GLOBAL_SIGNAL.requestAddPage.emit(
                timeseries._gid.str + "Visualization",
                lambda _: RegionalTimeSeriesPage(timeseries, self._subject),
            )

        elif isinstance(item, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                item._gid.str,
                lambda _: SurfacePage(item, f"{self._subject.name}-{name}"),
            )

        elif isinstance(item, Connectivity):
            GLOBAL_SIGNAL.requestAddPage.emit(
                item._gid.str,
                lambda _: ConnectivityPage(item),
            )

    def _click_analysis(self, item: Any):
        if isinstance(item, SimulationResult):
            timeseries = item.data[0]
            self._workspace = get_workspace()

            GLOBAL_SIGNAL.requestAddPage.emit(
                timeseries._gid.str + "Analysis",
                lambda _: AnalysisPage(timeseries, self._project),
            )

        elif isinstance(item, Surface):
            GLOBAL_SIGNAL.requestAddPage.emit(
                item._gid.str + "Analysis",
                lambda _: AnalysisPage(item, self._project),
            )

        elif isinstance(item, Connectivity):
            GLOBAL_SIGNAL.requestAddPage.emit(
                item._gid.str + "Analysis",
                lambda _: AnalysisPage(item, self._project),
            )

    def _widget_for_item(self, name: str, item: Any):
        widget = DataItem(name, item, FluentIcon.BOOK_SHELF, self)
        if isinstance(item, (SimulationResult, Surface, Connectivity)):
            widget.clicked.connect(partial(self._show_context_menu, widget))
        return widget
