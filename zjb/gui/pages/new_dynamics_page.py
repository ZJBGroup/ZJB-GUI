from pydantic import InstanceOf
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    IconWidget,
    LineEdit,
    PrimaryPushButton,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
)

from zjb.gui._global import get_workspace
from zjb.main.dtb.dynamics_model import (
    CouplingVariable,
    DynamicsModel,
    StateVariable,
    TransientVariable,
)
from zjb.main.manager.workspace import Workspace

from .._global import GLOBAL_SIGNAL
from ..common.utils import show_error, show_info, show_success
from ..widgets.new_dynamic_editor import BaseDynamicEditor
from .base_page import BasePage


class NewDynamicsPage(BasePage):
    def __init__(self, routeKey: str, parent=None):
        super().__init__(routeKey, routeKey, FluentIcon.CALORIES, parent)

        self.setObjectName(routeKey)
        self._setup_ui()
        self._window = parent
        self._workspace: Workspace = get_workspace()

        self.finish_btn.clicked.connect(self.create_model)

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 页面信息部分
        self.info_panel = QWidget(self)
        self.info_panel_layout = QHBoxLayout(self.info_panel)
        self.info_panel_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.pageicon = IconWidget(FluentIcon.CALORIES, self)
        self.pageicon.setFixedSize(60, 60)
        self.info_panel_layout.addWidget(self.pageicon)
        self.detail_panel = QWidget(self)
        self.detail_panel.setMinimumHeight(40)
        self.detail_panel_layout = QVBoxLayout(self.detail_panel)
        self.detail_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detail_panel_layout.setContentsMargins(10, 0, 0, 0)
        self.detail_panel_layout.addWidget(TitleLabel("New Dynamic Model"))
        self.detail_panel_layout.addWidget(
            BodyLabel(
                "Please fill in each item and submit the form to create a new Dynamic Model"
            )
        )
        self.info_panel_layout.addWidget(self.detail_panel)
        self.vBoxLayout.addWidget(self.info_panel)

        # 滚动区域部分
        self.scrollArea = SmoothScrollArea(self)
        self.vBoxLayout.addWidget(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)

        self.dynamic_name_editor = LineEdit(self)
        self.scrollLayout.addRow(
            SubtitleLabel("Dynamic Model Name:"), self.dynamic_name_editor
        )

        self.scrollLayout.addRow(SubtitleLabel("State Variables:"))
        self.state_variables_editor = BaseDynamicEditor(["name", "expression"])
        self.scrollLayout.addRow(self.state_variables_editor)

        self.scrollLayout.addRow(SubtitleLabel("Coupling Variables:"))
        self.coupling_variables_editor = BaseDynamicEditor(["name", "expression"])
        self.scrollLayout.addRow(self.coupling_variables_editor)

        self.scrollLayout.addRow(SubtitleLabel("Transient Variables:"))
        self.transient_variables_editor = BaseDynamicEditor(["name", "expression"])
        self.scrollLayout.addRow(self.transient_variables_editor)

        self.scrollLayout.addRow(SubtitleLabel("Parameters:"))
        self.parameters_editor = BaseDynamicEditor(["name", "value", "intro"])
        self.scrollLayout.addRow(self.parameters_editor)

        self.scrollLayout.addRow(SubtitleLabel("References:"))
        self.references_editor = BaseDynamicEditor(["detail"])
        self.scrollLayout.addRow(self.references_editor)

        self.vBoxLayout.addWidget(self.scrollArea)

        self.finish_btn = PrimaryPushButton("Create")
        self.finish_btn.setFixedWidth(150)
        self.scrollLayout.addRow(self.finish_btn)

    def create_model(self):
        """点击 Create 按钮创建 新的动力学模型"""
        model_dict = {}

        model_dict["name"] = self.dynamic_name_editor.text()
        model_dict["state_variables"] = self._format_date(
            self.state_variables_editor.getValue(), "state_variables"
        )
        model_dict["coupling_variables"] = self._format_date(
            self.coupling_variables_editor.getValue(), "coupling_variables"
        )
        model_dict["transient_variables"] = self._format_date(
            self.transient_variables_editor.getValue(), "transient_variables"
        )
        parameters_data = self._format_date_parameters(
            self.parameters_editor.getValue()
        )
        model_dict["parameters"] = parameters_data[0]
        model_dict["docs"] = parameters_data[1]

        model_dict["references"] = self.references_editor.getValue()

        # print("-----", model_dict)
        # mew_model = Instance(DynamicsModel, required=True)
        mew_model = DynamicsModel(
            name=model_dict["name"],
            state_variables=model_dict["state_variables"],
            coupling_variables=model_dict["coupling_variables"],
            transient_variables=model_dict["transient_variables"],
            parameters=model_dict["parameters"],
            docs=model_dict["docs"],
            references=model_dict["references"],
        )
        self._workspace.dynamics += [mew_model]
        show_success(f"Successfully created model:{model_dict['name']}", self._window)
        GLOBAL_SIGNAL.dynamicModelUpdate.emit(model_dict["name"])

    def _format_date(self, data, type=None):
        dict = {}
        if type == "state_variables":
            for item in data:
                dict.update({item[0]: StateVariable(expression=item[1])})
        if type == "coupling_variables":
            for item in data:
                dict.update({item[0]: CouplingVariable(expression=item[1])})
        if type == "transient_variables":
            for item in data:
                dict.update({item[0]: TransientVariable(expression=item[1])})

        return dict

    def _format_date_parameters(self, data):
        dict_parameters = {}
        dict_docs = {}
        for item in data:
            dict_parameters[item[0]] = float(item[1])
            dict_docs[item[0]] = item[2]

        return [dict_parameters, dict_docs]
