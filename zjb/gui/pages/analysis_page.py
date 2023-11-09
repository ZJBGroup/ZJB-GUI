import inspect

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBox,
    Dialog,
    FluentIcon,
    LineEdit,
    PrimaryPushButton,
    SmoothScrollArea,
    TitleLabel,
    TransparentDropDownPushButton,
    TransparentPushButton,
    MessageBoxBase
)

from zjb.main.api import (
    RegionalConnectivity,
    RegionalTimeSeries,
    SpaceSeries,
    TimeSeries,
    zjb_analysis,
)

from .._global import GLOBAL_SIGNAL, get_workspace
from ..widgets.mpl_widget import MplWidget

# from zjb.main.analysis import evaluation
from .base_page import BasePage
from .connectivity_page import ConnectivityPage
from .time_series_page import RegionalTimeSeriesPage


class AnalysisPage(BasePage):
    def __init__(self, data):
        super().__init__(data._gid.str + "Analysis", "Analysis", FluentIcon.DOCUMENT)
        self.data = data

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
            trait_content = self.data.trait_get()[trait_name]
            btn_trait = TransparentPushButton(f"{trait_content}")
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
                if parameter_type == TimeSeries:
                    cb_analysis.addItem(func_name)
                    break

        cb_analysis.currentIndexChanged.connect(lambda: _on_cb_analysis_changed())

        if compare:
            scrollLayout = QFormLayout()
            scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

            for trait_name in list(analysis_data.trait_get().keys()):
                trait_content = analysis_data.trait_get()[trait_name]
                btn_trait = TransparentPushButton(f"{trait_content}")
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
        vBoxLayout_2.addLayout(vBoxLayout_result)

        mplWidget = MplWidget()

        def _run_analysis():
            self._delete_all_in_layout(mplWidget.vertical_layout)
            self._delete_all_in_layout(vBoxLayout_result)

            analysis_func = eval("zjb_analysis." + cb_analysis.text())

            args = []
            args.append(analysis_data)
            signature_func = inspect.signature(analysis_func)
            for parameter in signature_func.parameters.values():
                parameter_name = parameter.name
                parameter_type = parameter.annotation
                if parameter_type == float:
                    exec(f"args.append(float(self.{parameter_name}_edit.text()))")
                elif parameter_type == str:
                    exec(f"args.append(self.{parameter_name}_edit.text())")
                elif parameter_type == int:
                    exec(f"args.append(int(self.{parameter_name}_edit.text()))")
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

                    if nrow == self.data.space.atlas.number_of_regions:
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
                        btn_save = TransparentPushButton("Save analysis result")
                        mplWidget.vertical_layout.addWidget(btn_save)

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

        def _on_cb_analysis_changed():
            self._delete_all_in_layout(mplWidget.vertical_layout)
            self._delete_all_in_layout(form_layout)
            self._delete_all_in_layout(vBoxLayout_result)

            analysis_func = eval("zjb_analysis." + cb_analysis.text())
            signature_func = inspect.signature(analysis_func)
            for parameter in signature_func.parameters.values():
                parameter_name = parameter.name
                parameter_type = parameter.annotation
                label = BodyLabel(f"{parameter_name}:")
                exec(f"self.{parameter_name}_edit = LineEdit()")
                if parameter.default is not inspect._empty:
                    exec(f"self.{parameter_name}_edit.setText(str(parameter.default))")
                else:
                    exec(
                        f"self.{parameter_name}_edit.setText(parameter.name + '.data')"
                    )
                    exec(f"self.{parameter_name}_edit.setEnabled(False)")

                hBoxLayout_cb = QHBoxLayout()
                hBoxLayout_cb.addWidget(label)
                # exec(f"hBoxLayout_cb.addWidget(self.{parameter_name}_edit)")
                exec(f"form_layout.addRow(label, self.{parameter_name}_edit)")

    def _compare_others(self):
        w = CompareDialog(self)
        # w.setTitleBarVisible(False)
        if w.exec():
            for project in get_workspace().children:
                for dtb in project.dtbs:
                    for data in dtb.data:
                        if data == w.combox_data.currentText():
                            compare_data = dtb.data[data].data[0]
        else:
            print("Cancel button is pressed")
        self._add_analysis(compare_data, compare=True)

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


class CompareDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._setup_ui()

    def _setup_ui(self):
        title = "Compare Data"
        content = """Choose data to analysis and compare with current results."""
        self.viewLayout.addWidget(TitleLabel(title))
        self.viewLayout.addWidget(BodyLabel(content))
        self.combox_data = ComboBox(self)
        for project in get_workspace().children:
            for dtb in project.dtbs:
                for data in dtb.data:
                    self.combox_data.addItem(data)
        self.viewLayout.addWidget(self.combox_data)

        self.cancelButton.hide()
