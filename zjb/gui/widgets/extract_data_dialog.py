from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    MessageBoxBase,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
    TransparentPushButton,
)
from zjb.main.api import DTB, Project, Subject

from .input_name_dialog import EntityCreationBase, SelectWidget
from .._global import get_workspace


class SelectData(EntityCreationBase):
    """选择数据"""

    def __init__(self, title: str, type="", project: Project = None, parent=None):
        super().__init__(title=title, type=type, project=project, parent=parent)

        # 隐藏不需要的命名框
        self.viewLayout.removeWidget(self.lineEdit)
        self.lineEdit.hide()

        # 所选项目中被试及dtb类目的下拉菜单
        subject_and_dtb_list = []
        subject_select_list = []
        dtb_select_list = []

        if project == None:
            subject_select_list = get_workspace().available_subjects()
            dtb_select_list = get_workspace().available_dtbs()
        else:
            subject_select_list = project.available_subjects()
            dtb_select_list = project.available_dtbs()
        subject_and_dtb_list = subject_select_list + dtb_select_list

        self.subject_and_dtb_selector = SelectWidget(
            "Subject and Dtb", dataList=subject_and_dtb_list
        )

        # data 下拉菜单
        data_select_list = []
        self.data_selector = SelectWidget("data", dataList=data_select_list)
        default_instance = self.subject_and_dtb_selector.getCurrentValue()
        if not default_instance == None:
            self._on_instance_list_changed(default_instance)

        self.viewLayout.addWidget(self.subject_and_dtb_selector)
        self.viewLayout.addWidget(self.data_selector)

        # 表单动态联动
        self.project_selector.selectedDateChanged.connect(self._on_project_list_changed)
        self.subject_and_dtb_selector.selectedDateChanged.connect(
            self._on_instance_list_changed
        )

    def _on_project_list_changed(self, project: Project):
        """选择不同的项目时，subject_and_dtb列表发生改变"""
        self.subject_and_dtb_selector.updateSelectList(
            project.available_subjects() + project.available_dtbs()
        )

    def _on_instance_list_changed(self, instance: Subject or DTB or Project):
        """选择不同的被试或数字孪生脑时，data列表发生改变"""
        data_items = []
        for key, value in instance.data.items():
            _item = {"name": key, "value": value}
            data_items.append(_item)

        # selected_project = self.project_selector.getCurrentValue()
        # for key, value in selected_project.data.items():
        #     _item = {"name": key, "value": value}
        #     data_items.append(_item)
        # data_items += selected_project.data

        self.data_selector.updateSelectList(data_items)

    def get_data(self):
        """外部控件获取选择的数据"""
        return self.data_selector.getCurrentValue()

    def get_subject_or_dtb(self):
        """外部控件获取选择的dtb或被试"""
        return self.subject_and_dtb_selector.getCurrentValue()


class PSEDataDialog(MessageBoxBase):
    """打开PSE数据后用于选择其中仿真结果的窗口"""

    def __init__(self, data, title: str, parent=None):
        super().__init__(parent=parent)
        self.data = data
        self.flag = ""
        self.title = title

        self._setup_ui()

    def _setup_ui(self):
        self.titleLabel = TitleLabel(self.title)
        self.titleLabel.setContentsMargins(0, 0, 0, 20)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.setSpacing(0)

        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.formLayout.addRow(SubtitleLabel("Parameters:"))

        for parameter in self.data.parameters:
            btn_parameter = TransparentPushButton(f"{self.data.parameters[parameter]}")
            self.formLayout.addRow(BodyLabel(parameter), btn_parameter)

        self.formLayout.addRow(SubtitleLabel("Data:"))

        self.scrollArea = SmoothScrollArea(self)

        self.scrollArea.setMinimumSize(650, 200)

        self.formLayout.addRow(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)

        self.scrollWidget = QWidget(self.scrollArea)

        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.parameter_selectors = {}
        # 构建参数输入框
        for parameter in self.data.parameters:
            self.parameter_selectors[parameter] = SelectWidget(
                parameter, dataList=self.data.parameters[parameter]
            )
            self.parameter_selectors[parameter].selectedDateChanged.connect(
                self._on_simulation_result_list_changed
            )
            self.scrollLayout.addRow(self.parameter_selectors[parameter])

            # _str_parameters_list = [str(n) for n in self.data.parameters[parameter]]
            # _selectlabel = QLabel(parameter, self)
            # _selectlabel.setFixedWidth(100)
            # _selectlabel.setStyleSheet("QLabel{font: 12px 'Microsoft YaHei';}")
            # _comboBox = ComboBox(self)
            # _comboBox.addItems(_str_parameters_list)
            # _layout = QHBoxLayout(self)
            # _layout.addWidget(_selectlabel)
            # _layout.addWidget(_comboBox)
            # self.scrollLayout.addRow(_layout)

        # 仿真结果 下拉菜单
        simulation_result_select_list = []
        self.simulation_result_selector = SelectWidget(
            "Simulation Result", dataList=simulation_result_select_list
        )

        self._on_simulation_result_list_changed()

        self.scrollLayout.addRow(self.simulation_result_selector)

        self.viewLayout.addLayout(self.formLayout)

        # 重写底部按钮
        self.yesButton.clicked.connect(lambda: self.submit_date("ok"))
        self.cancelButton.clicked.connect(lambda: self.submit_date("canel"))

    def submit_date(self, str):
        self.flag = str
        self.close()

    def getflag(self):
        return self.flag

    def get_data(self):
        """外部控件获取选择的数据"""
        return self.simulation_result_selector.getCurrentValue()

    def _on_simulation_result_list_changed(self):
        """选择PSE中不同参数的时候，simulation_result列表会进行改变"""
        simulation_result_select_list = []
        self._position = 1
        for parameter in self.data.parameters:
            # 通过计算不同参数数值在列表中的位置判断是第几个仿真结果
            if self.parameter_selectors[parameter].getCurrentValue() is None:
                return
            else:
                _value = self.parameter_selectors[parameter].getCurrentValue()
                self._position *= self.data.parameters[parameter].index(_value) + 1
                print(self._position)
        simulation_result_select_list.append(self.data.data[self._position - 1])
        self.simulation_result_selector.updateSelectList(simulation_result_select_list)
        # self.simulation_result_selector.


class SimulationResultDialog(MessageBoxBase):
    """打开SimulationResult数据后用于选择其中仿真结果的窗口"""

    def __init__(self, data, title: str, dtb: DTB = None, parent=None):
        super().__init__(parent=parent)
        self.dtb = dtb
        self.data = data
        self.flag = ""
        self.title = title

        self._setup_ui()

    def _setup_ui(self):
        self.titleLabel = TitleLabel(self.title)
        self.titleLabel.setContentsMargins(0, 0, 0, 20)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.setSpacing(0)

        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        if len(self.data.parameters) > 0:
            self.formLayout.addRow(SubtitleLabel("Parameters:"))

            for parameter in self.data.parameters:
                btn_parameter = TransparentPushButton(
                    f"{self.data.parameters[parameter]}"
                )
                self.formLayout.addRow(BodyLabel(parameter), btn_parameter)

        self.formLayout.addRow(SubtitleLabel("Data:"))

        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setMinimumSize(650, 100)

        self.formLayout.addRow(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)

        self.scrollWidget = QWidget(self.scrollArea)

        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # 监视器类型及检测的变量
        monitor_type_list = []
        monitor_variable_list = []
        for monitor in self.dtb.model.monitors:
            if monitor.__class__.__name__ not in monitor_type_list:
                monitor_type_list.append(monitor.__class__.__name__)
            monitor_variable_list.append(monitor.expression)

        self.monitor_type_selector = SelectWidget("Type", dataList=monitor_type_list)
        self.monitor_variable_selector = SelectWidget(
            "Variable", dataList=monitor_variable_list
        )

        self.monitor_type_selector.selectedDateChanged.connect(
            self._on_monitor_type_selector_changed
        )
        self.monitor_variable_selector.selectedDateChanged.connect(
            self._on_monitor_variable_selector_changed
        )

        # 时间序列 下拉菜单
        timeseries_list = []
        self.timeseries_selector = SelectWidget(
            "Simulation Result", dataList=timeseries_list
        )

        self._on_monitor_type_selector_changed()

        # 添加到布局
        self.scrollLayout.addRow(self.monitor_type_selector)
        self.scrollLayout.addRow(self.monitor_variable_selector)
        self.scrollLayout.addRow(self.timeseries_selector)

        self.viewLayout.addLayout(self.formLayout)

        # 重写底部按钮
        self.yesButton.clicked.connect(lambda: self.submit_date("ok"))
        self.cancelButton.clicked.connect(lambda: self.submit_date("canel"))

    def _on_timeseries_list_changed(self):
        """时间序列数据列表发生变化"""
        index = 0
        timeseries_list = []
        for monitor in self.dtb.model.monitors:
            if (
                monitor.expression == self.monitor_variable_selector.getCurrentValue()
                and monitor.__class__.__name__
                == self.monitor_type_selector.getCurrentValue()
            ):
                timeseries_list.append(self.data.data[index])
            index += 1
        self.timeseries_selector.updateSelectList(timeseries_list)

    def _on_monitor_type_selector_changed(self):
        """改变监视器类型的选项时，对应变量及时间序列列表发生改变"""
        index = 0
        variable_list = []
        for monitor in self.dtb.model.monitors:
            if (
                monitor.__class__.__name__
                == self.monitor_type_selector.getCurrentValue()
            ):
                variable_list.append(monitor.expression)
            index += 1
        self.monitor_variable_selector.updateSelectList(variable_list)
        self._on_timeseries_list_changed()

    def _on_monitor_variable_selector_changed(self):
        """pass"""
        # index = 0
        # timeseries_list = []
        # for monitor in self.dtb.model.monitors:
        #     if monitor.expression == self.monitor_type_selector.getCurrentValue():
        #         timeseries_list.append(self.data.data[index])
        #     index += 1
        # self.timeseries_selector.updateSelectList(timeseries_list)

        self._on_timeseries_list_changed()

    def submit_date(self, str):
        self.flag = str
        self.close()

    def getflag(self):
        return self.flag

    def get_timeseries_data(self):
        return self.timeseries_selector.getCurrentValue()
