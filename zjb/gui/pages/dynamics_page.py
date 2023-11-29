import copy
import traceback
import typing
import uuid
from functools import partial

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFormLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    LargeTitleLabel,
    SmoothScrollArea,
    StrongBodyLabel,
    SubtitleLabel,
    ToolTipFilter,
    ToolTipPosition,
)
from zjb.main.dtb.dynamics_model import (
    BifurcationFunc,
    BifurcationPlots,
    DynamicsModel,
    PhasePlaneFunc,
    PhasePlanePlots,
)
from zjb.main.dtb.utils import expression2unicode

from .._global import GLOBAL_SIGNAL
from ..common.utils import show_error, show_info, show_success
from ..widgets.bifurcation_widget_ui import Ui_bifurcation_widget
from ..widgets.editor import FloatEditor
from ..widgets.phase_plane_widget_ui import Ui_phase_plane_widget
from .base_page import BasePage
from .dynamics_page_ui import Ui_dynamics_page

DynamicsModelOrNone = typing.Optional[DynamicsModel]

expression2unicode_edit = partial(
    expression2unicode, rich=False
)  # 面对非Label类型时使用rich=False的函数


class DynamicsModelInfoPage(SmoothScrollArea):
    """展示动力学模型信息页"""

    _model: DynamicsModelOrNone

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.container = QWidget(self)
        self.setStyleSheet("QWidget {background-color: transparent;}")

        self.setWidget(self.container)
        self.setWidgetResizable(True)

        self.main_layout = QFormLayout(self.container)

        self._model = None

    def _update_variables(self, name: str, value):
        if not self._model:
            return
        model = self._model
        # model.observable_variables[name] = value
        self._model = model

    def _update_parameter(self, name: str, value):
        if not self._model:
            return
        model = self._model
        model.parameters[name] = value
        self._model = model

    def _update(self):
        if not self._model:
            return

        for i in reversed(range(self.main_layout.rowCount())):
            self.main_layout.removeRow(i)

        # observable_variables = self._model.observable_variables
        parameters = self._model.parameters
        docs = self._model.docs
        # expression = self._model.expression
        state_variables = self._model.state_variables
        transient_variables = self._model.transient_variables
        coupling_variables = self._model.coupling_variables

        self.main_layout.addRow(
            LargeTitleLabel(self._model.name + " Model"),
        )

        self.main_layout.addRow(
            SubtitleLabel("State Variables: "),
        )

        for name, value in state_variables.items():
            self.main_layout.addRow(
                BodyLabel(expression2unicode(f"d{name}/dt={value.expression}")),
            )

        self.main_layout.addRow(
            SubtitleLabel("Transient Variables: "),
        )

        for name, value in transient_variables.items():
            self.main_layout.addRow(
                BodyLabel(expression2unicode(f"{name}={value.expression}")),
            )

        self.main_layout.addRow(
            SubtitleLabel("Coupling Variables: "),
        )

        for name, value in coupling_variables.items():
            self.main_layout.addRow(
                BodyLabel(expression2unicode(f"{name}_i={value.expression}")),
            )

        self.main_layout.addRow(
            SubtitleLabel("Parameters: "),
        )

        for name, value in parameters.items():
            editor = FloatEditor(value)
            editor.setEnabled(False)
            editor.valueChanged.connect(partial(self._update_parameter, name))
            mylabel = BodyLabel(f"{expression2unicode(name)}:")
            mylabel.installEventFilter(
                ToolTipFilter(mylabel, 200, ToolTipPosition.LEFT)
            )
            mylabel.setToolTip(docs[name])
            self.main_layout.addRow(mylabel, editor)

        self.main_layout.addRow(
            SubtitleLabel("References: "),
        )

        for ref in self._model.references:
            ref_label = StrongBodyLabel()
            ref_label.setTextInteractionFlags(
                (Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            )
            ref_label.setWordWrap(True)
            ref_label.setText(ref)
            self.main_layout.addRow(
                ref_label,
            )


class PhasePlaneWorker(QThread):
    """分配线程处理相图分析任务"""

    # 定义一个信号，用于发送处理结果
    _resultReady = pyqtSignal(PhasePlanePlots)
    ppp = None
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def set_phase_plane_page(self, ppp):
        self.ppp = ppp

    def run(self):
        """加入按钮所需执行的相图分析代码，得到PhasePlanePlots类型的分析结果"""

        plt.close("all")

        try:
            pp = PhasePlaneFunc()
            pp.model = self.ppp._model

            dict_target_vars = {}
            dict_target_vars[
                self.ppp.available_variables[
                    self.ppp.ui.target_variable_x_cbb.currentIndex()
                ]
            ] = [
                float(self.ppp.ui.tvx_start_edit.text()),
                float(self.ppp.ui.tvx_end_edit.text()),
            ]
            dict_target_vars[
                self.ppp.available_variables[
                    self.ppp.ui.target_variable_x_cbb.currentIndex()
                    + 1
                    + self.ppp.ui.target_variable_y_cbb.currentIndex()
                ]
            ] = [
                float(self.ppp.ui.tvy_start_edit.text()),
                float(self.ppp.ui.tvy_end_edit.text()),
            ]

            pp.target_vars = dict_target_vars

            fixed_var = self.ppp.available_variables[:]
            fixed_var.remove(
                self.ppp.available_variables[
                    self.ppp.ui.target_variable_x_cbb.currentIndex()
                ]
            )
            fixed_var.remove(
                self.ppp.available_variables[
                    self.ppp.ui.target_variable_x_cbb.currentIndex()
                    + 1
                    + self.ppp.ui.target_variable_y_cbb.currentIndex()
                ]
            )
            dict_fixed_var = {}
            for fixed_var in fixed_var:
                dict_fixed_var[fixed_var] = 0

            pp.fixed_vars = dict_fixed_var

            dict_resolutions = {}
            dict_resolutions[
                self.ppp.available_variables[
                    self.ppp.ui.target_variable_x_cbb.currentIndex()
                ]
            ] = float(self.ppp.ui.tvx_step_edit.text())
            dict_resolutions[
                self.ppp.available_variables[
                    self.ppp.ui.target_variable_x_cbb.currentIndex()
                    + 1
                    + self.ppp.ui.target_variable_y_cbb.currentIndex()
                ]
            ] = float(self.ppp.ui.tvy_step_edit.text())

            pp.resolutions = dict_resolutions

            dict_trajectory = {}
            dict_trajectory[
                self.ppp.available_variables[
                    self.ppp.ui.target_variable_x_cbb.currentIndex()
                ]
            ] = [float(self.ppp.ui.trajectory_points_x_edit.text())]
            dict_trajectory[
                self.ppp.available_variables[
                    self.ppp.ui.target_variable_x_cbb.currentIndex()
                    + 1
                    + self.ppp.ui.target_variable_y_cbb.currentIndex()
                ]
            ] = [float(self.ppp.ui.trajectory_points_y_edit.text())]

            pp.trajectory = dict_trajectory
            pp.trajectory_duration = float(self.ppp.ui.trajectory_duration_edit.text())

            ppPlots = pp()
            self._resultReady.emit(ppPlots)  # 传出ppPlots

        except Exception as e:
            # 如果出现异常，获取异常的堆栈信息，并通过信号发送给主线程
            error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.error_signal.emit(error_msg)


class PhasePlanePage(SmoothScrollArea):
    """ """

    _model: DynamicsModelOrNone

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setStyleSheet("QWidget {background-color: transparent;}")

        self.setWidgetResizable(True)

        self.ui = Ui_phase_plane_widget()
        self.ui.setupUi(self)

        self.ui.start_btn.clicked.connect(self._start_phase_plane_worker)

        self.form_layout = QFormLayout()

        self._model = None

    def _update(self):
        if not self._model:
            return

        for i in reversed(range(self.form_layout.rowCount())):
            self.form_layout.removeRow(i)

        self.form_layout.addRow(LargeTitleLabel(self._model.name + " Model"))

        parameters = self._model.parameters

        self.form_layout.addRow(
            SubtitleLabel("Parameters: "),
        )

        for name, value in parameters.items():
            editor = FloatEditor(value)
            editor.valueChanged.connect(partial(self._update_parameter, name))
            self.form_layout.addRow(BodyLabel(f"{expression2unicode(name)}:"), editor)

        if not self._model:
            return

        self.ui.verticalLayout.insertLayout(0, self.form_layout)

        state_variables = self._model.state_variables
        transient_variables = self._model.transient_variables

        self.available_variables = list(state_variables.keys())
        self.available_variables_unicode = list(
            map(expression2unicode_edit, self.available_variables)
        )

        self.ui.target_variable_x_cbb.clear()
        self.ui.target_variable_y_cbb.clear()

        #  针对brainpy对于相平面分析中状态变量选择顺序的bug，在前端中做的限制
        # 第一个变量不能选最后一个
        for available_variables_name in self.available_variables_unicode[0:-1]:
            self.ui.target_variable_x_cbb.addItem(available_variables_name)

        index = self.ui.target_variable_x_cbb.currentIndex()

        for available_variables_name in self.available_variables_unicode[index + 1 :]:
            self.ui.target_variable_y_cbb.addItem(available_variables_name)

        self.ui.target_variable_x_cbb.currentIndexChanged.connect(
            self._on_target_variable_x_cbb_change
        )

    def _update_parameter(self, name: str, value):
        if not self._model:
            return
        model = self._model
        model.parameters[name] = value
        self._model = model

    def _on_target_variable_x_cbb_change(self, index):
        self.ui.target_variable_y_cbb.clear()
        # 第二个变量只能选第一个变量之后的变量
        for available_variables_name in self.available_variables_unicode[index + 1 :]:
            self.ui.target_variable_y_cbb.addItem(available_variables_name)

    def _start_phase_plane_worker(self):
        show_info("Start phase plane analysis......Please wait......", self.window())
        self.ui.start_btn.setEnabled(False)  # 禁用按钮

        self.phaseplaneworker = PhasePlaneWorker()
        self.phaseplaneworker.error_signal.connect(
            lambda msg: show_error(msg, self.window())
        )  # 如有报错，接收信息
        self.phaseplaneworker.error_signal.connect(
            lambda: self.ui.start_btn.setEnabled(True)
        )  # 如有报错，启用开始按钮
        self.phaseplaneworker.set_phase_plane_page(self)
        self.phaseplaneworker._resultReady.connect(self.update_phaseplane)
        self.phaseplaneworker.start()

    def update_phaseplane(self, ppPlots):
        for i in reversed(range(self.ui.pp_mplWidget.vertical_layout.count())):
            self.ui.pp_mplWidget.vertical_layout.removeWidget(
                self.ui.pp_mplWidget.vertical_layout.itemAt(i).widget().deleteLater()
            )
        canvas = FigureCanvas(ppPlots.figure)

        self.ui.pp_mplWidget.vertical_layout.addWidget(canvas)

        self.ui.fixed_points_edit.setText(str(ppPlots.fixed_points))
        self.ui.start_btn.setEnabled(True)  # 启用按钮


class BifurcationWorker(QThread):
    """分配线程处理分岔分析任务"""

    # 定义一个信号，用于发送处理结果
    _resultReady = pyqtSignal(BifurcationPlots)
    error_signal = pyqtSignal(str)
    bifurcation_plots = None

    def set_bifurcation_page(self, bifurcation_page):
        self.bifurcation_page = bifurcation_page

    def run(self):
        """加入按钮所需执行的分岔分析代码，得到BifurcationPlots类型的分析结果"""

        plt.close("all")
        try:
            bifurcation_func = BifurcationFunc()
            bifurcation_func.model = self.bifurcation_page._model

            dict_target_vars = {}
            dict_target_vars[
                self.bifurcation_page.available_variables[
                    self.bifurcation_page.ui.target_variable_x_cbb.currentIndex()
                ]
            ] = [
                float(self.bifurcation_page.ui.tvx_start_edit.text()),
                float(self.bifurcation_page.ui.tvx_end_edit.text()),
            ]
            dict_target_vars[
                self.bifurcation_page.available_variables[
                    self.bifurcation_page.ui.target_variable_y_cbb.currentIndex()
                ]
            ] = [
                float(self.bifurcation_page.ui.tvy_start_edit.text()),
                float(self.bifurcation_page.ui.tvy_end_edit.text()),
            ]

            bifurcation_func.target_vars = dict_target_vars

            fixed_var = self.bifurcation_page.available_variables[:]
            fixed_var.remove(
                self.bifurcation_page.available_variables[
                    self.bifurcation_page.ui.target_variable_x_cbb.currentIndex()
                ]
            )
            fixed_var.remove(
                self.bifurcation_page.available_variables[
                    self.bifurcation_page.ui.target_variable_y_cbb.currentIndex()
                ]
            )
            dict_fixed_var = {}
            for fixed_var in fixed_var:
                dict_fixed_var[fixed_var] = 0

            bifurcation_func.fixed_vars = dict_fixed_var

            dict_target_pars = {}
            dict_target_pars[
                self.bifurcation_page.parameters[
                    self.bifurcation_page.ui.target_parameter_x_cbb.currentIndex()
                ]
            ] = [
                float(self.bifurcation_page.ui.tpx_start_edit.text()),
                float(self.bifurcation_page.ui.tpx_end_edit.text()),
            ]
            dict_target_pars[
                self.bifurcation_page.parameters[
                    self.bifurcation_page.ui.target_parameter_y_cbb.currentIndex()
                ]
            ] = [
                float(self.bifurcation_page.ui.tpy_start_edit.text()),
                float(self.bifurcation_page.ui.tpy_end_edit.text()),
            ]

            bifurcation_func.target_pars = dict_target_pars

            dict_resolutions = {}
            dict_resolutions[
                self.bifurcation_page.parameters[
                    self.bifurcation_page.ui.target_parameter_x_cbb.currentIndex()
                ]
            ] = float(self.bifurcation_page.ui.tpx_step_edit.text())
            dict_resolutions[
                self.bifurcation_page.parameters[
                    self.bifurcation_page.ui.target_parameter_y_cbb.currentIndex()
                ]
            ] = float(self.bifurcation_page.ui.tpy_step_edit.text())

            bifurcation_func.resolutions = dict_resolutions

            bifurcationPlots = bifurcation_func(show=False)

            self._resultReady.emit(bifurcationPlots)  # 传出bifurcationPlots

        except Exception as e:
            # 如果出现异常，获取异常的堆栈信息，并通过信号发送给主线程
            error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.error_signal.emit(error_msg)


class BifurcationPage(SmoothScrollArea):
    _model: DynamicsModelOrNone

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setStyleSheet("QWidget {background-color: transparent;}")

        self.setWidgetResizable(True)

        self.ui = Ui_bifurcation_widget()
        self.ui.setupUi(self)

        self.ui.start_btn.clicked.connect(self._start_bifurcation_worker)

        self.form_layout = QFormLayout()

        self._model = None

    def _update(self):
        for i in reversed(range(self.form_layout.rowCount())):
            self.form_layout.removeRow(i)

        self.form_layout.addRow(LargeTitleLabel(self._model.name + " Model"))

        parameters = self._model.parameters

        self.form_layout.addRow(
            SubtitleLabel("Parameters: "),
        )

        for name, value in parameters.items():
            editor = FloatEditor(value)
            editor.valueChanged.connect(partial(self._update_parameter, name))
            self.form_layout.addRow(BodyLabel(f"{expression2unicode(name)}:"), editor)

        if not self._model:
            return

        self.ui.verticalLayout.insertLayout(0, self.form_layout)

        state_variables = self._model.state_variables
        transient_variables = self._model.transient_variables
        self.parameters = list(self._model.parameters.keys())
        parameters_unicode = list(map(expression2unicode_edit, self.parameters))

        self.available_variables = list(state_variables.keys())
        self.available_variables_unicode = list(
            map(expression2unicode_edit, self.available_variables)
        )
        self.ui.target_variable_x_cbb.clear()
        self.ui.target_variable_y_cbb.clear()
        self.ui.target_parameter_x_cbb.clear()
        self.ui.target_parameter_y_cbb.clear()

        for available_variables_name in self.available_variables_unicode:
            self.ui.target_variable_x_cbb.addItem(available_variables_name)
            self.ui.target_variable_y_cbb.addItem(available_variables_name)
        for parameters_name in parameters_unicode:
            self.ui.target_parameter_x_cbb.addItem(parameters_name)
            self.ui.target_parameter_y_cbb.addItem(parameters_name)

    def _update_parameter(self, name: str, value):
        if not self._model:
            return
        model = self._model
        model.parameters[name] = value
        self._model = model

    def _start_bifurcation_worker(self):
        show_info("Start bifurcation analysis......Please wait......", self.window())
        self.ui.start_btn.setEnabled(False)  # 禁用按钮

        self.bifurcation_worker = BifurcationWorker()
        self.bifurcation_worker.error_signal.connect(
            lambda msg: show_error(msg, self.window())
        )  # 如有报错，接收信息
        self.bifurcation_worker.error_signal.connect(
            lambda: self.ui.start_btn.setEnabled(True)
        )  # 如有报错，启用开始按钮
        self.bifurcation_worker.set_bifurcation_page(self)
        self.bifurcation_worker._resultReady.connect(self.update_bifurcation)
        self.bifurcation_worker.start()

    def update_bifurcation(self, bifurcationPlots):
        for i in reversed(range(self.ui.bif_mplWidget.vertical_layout.count())):
            self.ui.bif_mplWidget.vertical_layout.removeWidget(
                self.ui.bif_mplWidget.vertical_layout.itemAt(i).widget().deleteLater()
            )

        for i in reversed(range(self.ui.bif_mplWidget_2.vertical_layout.count())):
            self.ui.bif_mplWidget_2.vertical_layout.removeWidget(
                self.ui.bif_mplWidget_2.vertical_layout.itemAt(i).widget().deleteLater()
            )

        canvas = FigureCanvas(bifurcationPlots.figure)
        canvas_2 = FigureCanvas(bifurcationPlots.figure2)

        # canvas.setMinimumSize(1000,500)
        # canvas_2.setMinimumSize(1000,500)

        self.ui.bif_mplWidget.vertical_layout.addWidget(canvas)
        self.ui.bif_mplWidget_2.vertical_layout.addWidget(canvas_2)

        self.ui.start_btn.setEnabled(True)  # 启用按钮


class DynamicsInformationPage(BasePage):
    _model: DynamicsModelOrNone

    def __init__(
        self, routeKey: str, title: str, icon, dynamicsModel, index, parent=None
    ):
        super().__init__(routeKey, title, icon, parent)

        self._model = dynamicsModel
        self.index = index
        self.pp_page_num = 1
        self.bif_page_num = 1

        self._setup_ui()

        self.setObjectName(routeKey)

    def _setup_ui(self):
        self.ui = Ui_dynamics_page()
        self.ui.setupUi(self)

        self._init_dm_into_page()
        self._init_phase_plane_page()
        self._init_bifurcation_page()
        self._setModel(self._model)
        self._init_config()

        self.ui.dm_info_button.clicked.connect(self.display)
        self.ui.phase_plane_analysis_button.clicked.connect(self.display)
        self.ui.bifurcation_analysis_button.clicked.connect(self.display)

    def _init_config(self):
        self.ui.stackedWidget.setCurrentIndex(self.index)
        if self.index == 0:
            self.ui.phase_plane_analysis_button.setChecked(False)
            self.ui.bifurcation_analysis_button.setChecked(False)
            self.ui.dm_info_button.setChecked(True)

        elif self.index == 1:
            self.ui.phase_plane_analysis_button.setChecked(True)
            self.ui.bifurcation_analysis_button.setChecked(False)
            self.ui.dm_info_button.setChecked(False)

        elif self.index == 2:
            self.ui.phase_plane_analysis_button.setChecked(False)
            self.ui.bifurcation_analysis_button.setChecked(True)
            self.ui.dm_info_button.setChecked(False)

    def _init_dm_into_page(self):
        "设置动力学模型信息页"
        self.dynamic_model_info_page = DynamicsModelInfoPage()
        self.ui.dm_info_page_verticalLayout.addWidget(self.dynamic_model_info_page)

    def _init_phase_plane_page(self):
        "设置相图分析页"
        self.phase_plane_page = PhasePlanePage()
        self.ui.phase_plane_page_verticalLayout.addWidget(self.phase_plane_page)

    def _init_bifurcation_page(self):
        "设置分岔分析页"
        self.bifurcation_page = BifurcationPage()
        self.ui.bifurcation_page_verticalLayout.addWidget(self.bifurcation_page)

    def display(self):
        sender = self.sender()
        if sender.text() == "Dynamic Model Infomation":
            self.ui.dm_info_button.setChecked(not self.ui.dm_info_button.isChecked())

            GLOBAL_SIGNAL.requestAddPage.emit(self._model.name, self._addpage)

            self.index = 0

        elif sender.text() == "Phase Plane Analysis":
            self.ui.phase_plane_analysis_button.setChecked(
                not self.ui.phase_plane_analysis_button.isChecked()
            )
            self.index = 1
            GLOBAL_SIGNAL.requestAddPage.emit(str(uuid.uuid1()), self._addpage)

        elif sender.text() == "Bifurcation Analysis":
            self.ui.bifurcation_analysis_button.setChecked(
                not self.ui.bifurcation_analysis_button.isChecked()
            )
            self.index = 2
            GLOBAL_SIGNAL.requestAddPage.emit(str(uuid.uuid1()), self._addpage)

    def _addpage(self, routeKey: str):
        if self.index == 1:
            _page = DynamicsInformationPage(
                routeKey,
                "PhasePlane for" + self._model.name,
                FluentIcon.ROBOT,
                self._model,
                self.index,
            )
        elif self.index == 2:
            _page = DynamicsInformationPage(
                routeKey,
                "Bifurcation for" + self._model.name,
                FluentIcon.ROBOT,
                self._model,
                self.index,
            )
        return _page

    def _setModel(self, model: DynamicsModelOrNone):
        """设置要编辑的动力学模型"""
        self.dynamic_model_info_page._model = copy.deepcopy(model)
        self.dynamic_model_info_page._update()
        self.phase_plane_page._model = copy.deepcopy(model)
        self.phase_plane_page._update()
        self.bifurcation_page._model = copy.deepcopy(model)
        self.bifurcation_page._update()
        self.ui.dm_info_button.click()
