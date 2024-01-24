import inspect
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBox,
    FluentIcon,
    LineEdit,
    MessageBoxBase,
    PrimaryPushButton,
    SmoothScrollArea,
    TitleLabel,
    TransparentPushButton,
)

from zjb.main.api import (
    AnalysisResult,
    RegionalConnectivity,
    RegionalTimeSeries,
    zjb_analysis,
    PSEResult,
    SimulationResult,
)
# from zjb.main.analysis import evaluation
from .base_page import BasePage
from .connectivity_page import ConnectivityPage
from .time_series_page import RegionalTimeSeriesPage
from .._global import GLOBAL_SIGNAL, get_workspace
from ..widgets.extract_data_dialog import PSEDataDialog, SimulationResultDialog
from ..widgets.extract_data_dialog import SelectData
from ..widgets.mpl_widget import MplWidget

# 导入exec中使用的函数，避免优化导入自动删除
exec("from functools import partial")


class AnalysisPage(BasePage):
    def __init__(self, data, project):
        super().__init__(data._gid.str + "Analysis", "Analysis", FluentIcon.DOCUMENT)
        self.data = data
        self.project = project

        self._setup_ui()

        self.setObjectName(data._gid.str + "Analysis")

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self)

        self.spacerItem = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.hBoxLayout.addWidget(TitleLabel("Analysis"))

        btn_add = PrimaryPushButton(f"Add Data Analysis")
        btn_add.clicked.connect(lambda: self._add_analysis(self.data))
        self.hBoxLayout.addWidget(btn_add)

        btn_compare = PrimaryPushButton(f"Compare with others")
        btn_compare.clicked.connect(self._compare_others)
        self.hBoxLayout.addWidget(btn_compare)

        # btn_conjoint = PrimaryPushButton(f"Analysis with others")
        # btn_conjoint.clicked.connect(self._analysis_with_others)
        # self.hBoxLayout.addWidget(btn_conjoint)

        self.hBoxLayout.addStretch()

        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.scrollArea = SmoothScrollArea(self)
        self.vBoxLayout.addWidget(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        for trait_name in list(self.data.trait_get().keys()):
            btn_trait = self._create_data_button(
                trait_name, self.data.trait_get()[trait_name]
            )
            self.scrollLayout.addRow(BodyLabel(trait_name + ": "), btn_trait)

        self.scrollLayout.addItem(self.spacerItem)

    def _add_analysis(self, analysis_data, compare=False):
        self.scrollLayout.removeItem(self.spacerItem)

        cardWidget_analysis = CardWidget()
        cardWidget_analysis.minimumSize()
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            cardWidget_analysis.sizePolicy().hasHeightForWidth()
        )
        cardWidget_analysis.setSizePolicy(sizePolicy)

        hBoxLayout = QHBoxLayout(cardWidget_analysis)

        vBoxLayout_1 = QVBoxLayout()

        if compare:
            btn_text = "Run Comparison"
        else:
            btn_text = "Run Analysis"
        btn_run = PrimaryPushButton(btn_text)
        btn_run.clicked.connect(lambda: _run_analysis())

        vBoxLayout_1.addWidget(btn_run)
        vBoxLayout_1.addStretch()

        widget = QWidget(cardWidget_analysis)
        hBoxLayout_2 = QHBoxLayout(widget)
        vBoxLayout_2 = QVBoxLayout()
        hBoxLayout_2.addLayout(vBoxLayout_2)

        form_layout = QFormLayout()
        hBoxLayout_2.addLayout(form_layout)

        cb_analysis = ComboBox()
        cb_analysis.addItem("Please select an analysis method")
        for func_name in zjb_analysis.__all__:
            func = eval("zjb_analysis." + func_name)
            signature = inspect.signature(func)
            for parameter in signature.parameters.values():
                parameter_name = parameter.name
                parameter_type = parameter.annotation
                if isinstance(analysis_data, parameter_type):
                    cb_analysis.addItem(func_name)
                    analysis_input = analysis_data
                    break
                elif isinstance(analysis_data.data, parameter_type):
                    cb_analysis.addItem(func_name)
                    analysis_input = analysis_data.data
                    break

        cb_analysis.currentIndexChanged.connect(
            lambda: _on_cb_analysis_changed(analysis_data)
        )

        if compare:
            scrollLayout = QFormLayout()
            scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

            for trait_name in list(analysis_data.trait_get().keys()):
                btn_trait = self._create_data_button(
                    trait_name, analysis_data.trait_get()[trait_name]
                )
                scrollLayout.addRow(BodyLabel(trait_name + ": "), btn_trait)
            vBoxLayout_2.addLayout(scrollLayout)

        vBoxLayout_2.addWidget(cb_analysis)
        vBoxLayout_2.addStretch()

        hBoxLayout.addLayout(vBoxLayout_1)
        hBoxLayout.addWidget(widget)

        hBoxLayout.addStretch()

        self.scrollLayout.addRow(cardWidget_analysis)
        self.scrollLayout.addItem(self.spacerItem)

        vBoxLayout_result = QVBoxLayout()

        mplWidget = MplWidget()

        def _run_analysis():
            self._delete_all_in_layout(mplWidget.vertical_layout)
            self._delete_all_in_layout(vBoxLayout_result)

            analysis_func = eval("zjb_analysis." + cb_analysis.text())

            args = []
            # args.append(analysis_input)
            print(analysis_input)
            signature_func = inspect.signature(analysis_func)
            for parameter in signature_func.parameters.values():
                parameter_name = parameter.name
                parameter_type = parameter.annotation
                if parameter.default is not inspect._empty:
                    exec(
                        f"args.append(parameter_type(self.{parameter_name}_edit.text()))"
                    )

                    # if parameter_type == float:
                    #     exec(f"args.append(float(self.{parameter_name}_edit.text()))")
                    # elif parameter_type == str:
                    #     exec(f"args.append(self.{parameter_name}_edit.text())")
                    # elif parameter_type == int:
                    #     exec(f"args.append(int(self.{parameter_name}_edit.text()))")
                else:
                    # exec(f"args.append(parameter_type(self.{parameter_name}_edit.text()))")
                    exec(
                        f"""
_parameter  = self._{parameter_name}
if isinstance(_parameter, parameter_type):
    args.append(_parameter)

elif isinstance(_parameter.data[0], parameter_type):
    args.append(_parameter.data[0])
                    """
                    )

            args = tuple(args)
            result = analysis_func(*args)
            if result.ndim == 2:
                nrow, ncol = result.shape
                if nrow == ncol:
                    fig = plt.figure()
                    canvas = FigureCanvas(fig)
                    ax = fig.add_axes(111)
                    c = ax.matshow(result)
                    fig.colorbar(c, ax=ax, location="right")
                    mplWidget.vertical_layout.addWidget(canvas)
                    vBoxLayout_2.addWidget(mplWidget)

                    if (
                        hasattr(self.data, "space")
                        and nrow == self.data.space.atlas.number_of_regions
                    ):
                        analysis_result = RegionalConnectivity(
                            space=self.data.space,
                            data=result,
                        )
                        btn_show = TransparentPushButton("Advanced Visualization")
                        btn_show.clicked.connect(lambda: _add_advanced_vispage())

                        def _add_advanced_vispage():
                            GLOBAL_SIGNAL.requestAddPage.emit(
                                analysis_result._gid.str,
                                lambda _: ConnectivityPage(analysis_result),
                            )

                        mplWidget.vertical_layout.addWidget(btn_show)

                    elif (
                        hasattr(self.data.origin[0], "space")
                        and nrow == self.data.origin[0].space.atlas.number_of_regions
                    ):
                        analysis_result = RegionalConnectivity(
                            space=self.data.origin[0].space,
                            data=result,
                        )
                        btn_show = TransparentPushButton("Advanced Visualization")
                        btn_show.clicked.connect(lambda: _add_advanced_vispage())

                        def _add_advanced_vispage():
                            GLOBAL_SIGNAL.requestAddPage.emit(
                                analysis_result._gid.str,
                                lambda _: ConnectivityPage(analysis_result),
                            )

                        mplWidget.vertical_layout.addWidget(btn_show)

                else:
                    fig = plt.figure()
                    canvas = FigureCanvas(fig)
                    ax = fig.add_axes(111)
                    ax.plot(result)
                    mplWidget.vertical_layout.addWidget(canvas)
                    vBoxLayout_2.addWidget(mplWidget)

                    if ncol == self.data.space.atlas.number_of_regions:
                        analysis_result = RegionalTimeSeries(
                            space=self.data.space,
                            data=result,
                            sample_unit=self.data.sample_unit,
                        )
                        btn_show = TransparentPushButton("Advanced Visualization")
                        btn_show.clicked.connect(lambda: _add_advanced_vispage())

                        def _add_advanced_vispage():
                            for subject_ws in get_workspace().subjects:
                                if subject_ws.name == "fsaverage":
                                    subject = subject_ws

                            GLOBAL_SIGNAL.requestAddPage.emit(
                                analysis_result._gid.str,
                                lambda _: RegionalTimeSeriesPage(
                                    analysis_result, subject
                                ),
                            )

                        mplWidget.vertical_layout.addWidget(btn_show)
                        btn_save = TransparentPushButton("Save analysis result")
                        mplWidget.vertical_layout.addWidget(btn_save)

            else:
                btn_result = TransparentPushButton(f"{result}")

                vBoxLayout_result.addWidget(btn_result)

            analysis_parameters = {}
            analysis_parameters["Analysis Method"] = cb_analysis.text()

            for parameter in signature_func.parameters.values():
                parameter_name = parameter.name
                parameter_type = parameter.annotation
                if parameter_type == float:
                    exec(
                        f"analysis_parameters[parameter_name] = float(self.{parameter_name}_edit.text())"
                    )
                elif parameter_type == str:
                    exec(
                        f"analysis_parameters[parameter_name] = self.{parameter_name}_edit.text()"
                    )
                elif parameter_type == int:
                    exec(
                        f"analysis_parameters[parameter_name] = int(self.{parameter_name}_edit.text())"
                    )
                else:
                    exec(
                        f"analysis_parameters[parameter_name] = str(self.{parameter_name}_edit.text())"
                    )

            analysises = AnalysisResult(
                origin=[
                    self.data,
                ],
                data=result,
                parameters=analysis_parameters,
            )

            btn_save = TransparentPushButton("Save analysis result")
            btn_save.clicked.connect(lambda: self._save_analysises(analysises))
            vBoxLayout_result.addWidget(btn_save)

            vBoxLayout_2.addLayout(vBoxLayout_result)

        def _on_cb_analysis_changed(analysis_data):
            self._delete_all_in_layout(mplWidget.vertical_layout)
            self._delete_all_in_layout(form_layout)
            self._delete_all_in_layout(vBoxLayout_result)

            analysis_func = eval("zjb_analysis." + cb_analysis.text())
            signature_func = inspect.signature(analysis_func)
            #
            # for parameter in signature_func.parameters.values():
            #     parameter_name = parameter.name
            #     parameter_type = parameter.annotation
            #     if isinstance(analysis_data, parameter_type):
            #         analysis_input = analysis_data
            #
            #     elif isinstance(analysis_data.data, parameter_type):
            #         cb_analysis.addItem(func_name)
            #         analysis_input = analysis_data.data

            for parameter in signature_func.parameters.values():
                parameter_name = parameter.name
                parameter_type = parameter.annotation
                label = BodyLabel(f"{parameter_name}:")
                exec(
                    f"""
self.{parameter_name}_edit = LineEdit()
self.{parameter_name}_edit.setMinimumWidth(350)
                    """
                )
                if parameter.default is not inspect._empty:
                    if parameter.default == "Path":
                        exec(
                            f"""
self.{parameter_name}_edit.setText(str(parameter.default))
self.{parameter_name}_sf_btn = TransparentPushButton('select file')
self.{parameter_name}_sf_btn.clicked.connect(partial(self._select_file, self.{parameter_name}_edit))
form_layout.addRow(label, self.{parameter_name}_edit)
form_layout.addRow(self.{parameter_name}_sf_btn)
                            """
                        )
                        pass
                    else:
                        exec(
                            f"self.{parameter_name}_edit.setText(str(parameter.default))"
                        )
                        exec(f"form_layout.addRow(label, self.{parameter_name}_edit)")
                else:
                    exec(
                        f"""
self.{parameter_name}_btn = TransparentPushButton('Load')
self.{parameter_name}_btn.clicked.connect(partial(self._load_conjoint, '{parameter_name}'))
self.{parameter_name}_edit.setText('current data')   
if isinstance(analysis_data, parameter_type):
    analysis_input = analysis_data

elif isinstance(analysis_data.data, parameter_type):
    analysis_input = analysis_data.data
self._{parameter_name} = analysis_input    
self.{parameter_name}_edit.setEnabled(False)            
form_layout.addRow(label, self.{parameter_name}_edit)
form_layout.addRow(self.{parameter_name}_btn)
                        """,
                    )

    def _compare_others(self):
        w = CompareDialog(self.project, self)
        if w.exec():
            for dtb in self.project.dtbs:
                for simulation_result in dtb.data:
                    for data in dtb.data[simulation_result].data:
                        if data._gid.str == w.combox_data.currentText():
                            compare_data = data

            for data in self.project.data:
                if isinstance(data, AnalysisResult):
                    if data.name == w.combox_data.currentText():
                        compare_data = data

            self._add_analysis(compare_data, compare=True)

        else:
            print("Cancel button is pressed")

    def _analysis_with_others(self):
        w = ConjointDialog(self.project, self)
        if w.exec():
            for dtb in self.project.dtbs:
                for simulation_result in dtb.data:
                    for data in dtb.data[simulation_result].data:
                        if data._gid.str == w.combox_data.currentText():
                            conjoint_data = data

            for data in self.project.data:
                if isinstance(data, AnalysisResult):
                    if data.name == w.combox_data.currentText():
                        conjoint_data = data

    def _delete_all_in_layout(self, thisLayout):
        item_list = list(range(thisLayout.count()))
        item_list.reverse()

        for i in item_list:
            item = thisLayout.itemAt(i)
            if item is not None:
                if item.widget() is not None:
                    item.widget().deleteLater()
                elif isinstance(item, QSpacerItem):
                    thisLayout.removeItem(item)
                else:
                    self._delete_all_in_layout(item.layout())
                thisLayout.removeItem(item)

    def _show_trait_data(self, name, data):
        w = ShowDataDialog(name, data, self)
        w.exec()

    def _create_data_button(self, trait_name, data):
        trait_content = data
        btn_trait = TransparentPushButton(f"{trait_content}")
        btn_trait.setMaximumSize(10000, 100)
        btn_trait.clicked.connect(
            lambda: self._show_trait_data(trait_name, str(trait_content))
        )
        return btn_trait

    def _save_analysises(self, analysises):
        dialog = SelectData(
            "Choose the dtb or subject you want to save the analysis result",
            "",
            self.project,
            self,
        )
        dialog.data_selector.hide()
        dialog.exec()
        if dialog.getflag() == "canel":
            _get_subject_or_dtb = "canel"
        else:
            print(1)
            _get_subject_or_dtb = dialog.get_subject_or_dtb()
        dialog = SaveResultDialog(self)
        dialog.exec()
        analysises.name = dialog.edit_name.text()
        _get_subject_or_dtb.data |= {analysises.name: analysises}

    def _load_conjoint(self, parameter_name):
        print(parameter_name)
        # dialog = EntityCreationBase("aaa", "a", self.project, self)
        dialog = SelectData("Select Data", "", self.project, self)
        _getdata = False
        dialog.exec()
        if dialog.getflag() == "canel":
            _getdata = "canel"
        else:
            _getdata = dialog.get_data()
            _get_subject_or_dtb = dialog.get_subject_or_dtb()

        if _getdata == "canel":
            return
        elif isinstance(_getdata, PSEResult):
            pse_data_dialog = PSEDataDialog(_getdata, "PSE data", self)
            pse_data_dialog.exec()

            if pse_data_dialog.getflag() == "canel":
                _getdata = "canel"
            else:
                _getdata = pse_data_dialog.get_data()

            if _getdata == "canel":
                return

        if isinstance(_getdata, SimulationResult):
            simulation_result_dialog = SimulationResultDialog(
                _getdata, "Simulation data", _get_subject_or_dtb, self
            )
            simulation_result_dialog.exec()

            if simulation_result_dialog.getflag() == "canel":
                _getdata = "canel"
            else:
                _getdata = simulation_result_dialog.get_timeseries_data()

        exec(f"self._{parameter_name} = _getdata")
        exec(f"self.{parameter_name}_edit.setText(str(_getdata))  ")

    def _select_file(self, lineedit):
        window = QWidget()
        file_path, _ = QFileDialog.getOpenFileName(
            window, "select file", "./", "All Files (*)"
        )

        if file_path:
            lineedit.setText(file_path)


class CompareDialog(MessageBoxBase):
    def __init__(self, project, parent=None):
        super().__init__(parent=parent)
        self.project = project
        self._setup_ui()

    def _setup_ui(self):
        title = "Compare Data"
        content = """Choose data to analysis and compare with current results."""
        self.viewLayout.addWidget(TitleLabel(title))
        self.viewLayout.addWidget(BodyLabel(content))
        self.combox_data = ComboBox(self)

        for dtb in self.project.dtbs:
            for simulation_result in dtb.data:
                for data in dtb.data[simulation_result].data:
                    self.combox_data.addItem(data._gid.str)

        # for subject in self.project.subjects:
        #     for name, data in subject:
        #         self.combox_data.addItem(data)

        for analysis_result in self.project.data:
            if isinstance(analysis_result, AnalysisResult):
                self.combox_data.addItem(analysis_result.name)

        self.viewLayout.addWidget(self.combox_data)

        self.cancelButton.hide()


class ShowDataDialog(MessageBoxBase):
    def __init__(self, name, data, parent=None):
        super().__init__(parent=parent)
        self.trait_name = name
        self.trait_data = data
        self._setup_ui()

    def _setup_ui(self):
        self.viewLayout.addWidget(TitleLabel(self.trait_name))
        self.viewLayout.addWidget(BodyLabel(f"{self.trait_data}"))

        self.cancelButton.hide()


class SaveResultDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._setup_ui()

    def _setup_ui(self):
        self.viewLayout.addWidget(TitleLabel("Name the analysis result:"))
        self.edit_name = LineEdit()
        self.viewLayout.addWidget(self.edit_name)

        # self.cancelButton.hide()


class ConjointDialog(MessageBoxBase):
    def __init__(self, project, parent=None):
        super().__init__(parent=parent)
        self.project = project
        self._setup_ui()

    def _setup_ui(self):
        title = "Compare Data"
        content = """Choose data to analysis with current data."""
        self.viewLayout.addWidget(TitleLabel(title))
        self.viewLayout.addWidget(BodyLabel(content))
        self.combox_data = ComboBox(self)

        for dtb in self.project.dtbs:
            for simulation_result in dtb.data:
                for data in dtb.data[simulation_result].data:
                    self.combox_data.addItem(data._gid.str)

        # for dtb in self.project.dtbs:
        #     for item in dtb.data.items():
        #         for data in item[1]:
        #             self.combox_data.addItem(data._gid.str)

        # for subject in self.project.subjects:
        #     for name in subject.data:
        #         print(name)
        #         print(subject.data[name])
        #         if isinstance(subject.data[name], Connectivity):
        #             print(subject.data[name]._gid.str)
        #             self.combox_data.addItem(subject.data[name]._gid.str)

        for subject in self.project.subjects:
            for item in subject.data.items():
                self.combox_data.addItem(item[0])

        for subject in self.project.parent.subjects:
            for item in subject.data.items():
                self.combox_data.addItem(item[0])

        for analysis_result in self.project.data:
            if isinstance(analysis_result, AnalysisResult):
                self.combox_data.addItem(analysis_result.name)

        self.viewLayout.addWidget(self.combox_data)

        # self.cancelButton.hide()
