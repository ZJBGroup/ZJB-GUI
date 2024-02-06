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
from ..common.utils import show_error, show_success
from ..widgets.new_dynamic_editor import BaseDynamicEditor
from .base_page import BasePage


class NewDynamicsPage(BasePage):
    def __init__(self, routeKey: str, model_name: str, parent=None):
        super().__init__(routeKey, routeKey, FluentIcon.CALORIES, parent)
        self.setObjectName(routeKey)
        self._setup_ui()
        self._window = parent
        self._workspace: Workspace = get_workspace()
        self.finish_btn.clicked.connect(self.create_model)

        self.select_dynamicsModel = None
        for dynamicsModel in self._workspace.dynamics:
            if dynamicsModel.name == model_name:
                self.select_dynamicsModel = dynamicsModel
                break
        if self.select_dynamicsModel:
            self.set_format_data(self.select_dynamicsModel)

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
        # Dynamic Model Name
        self.dynamic_name_editor = LineEdit(self)
        self.scrollLayout.addRow(
            SubtitleLabel("Dynamic Model Name:"), self.dynamic_name_editor
        )
        # State Variables
        self.scrollLayout.addRow(SubtitleLabel("State Variables:"))
        self.state_variables_editor = BaseDynamicEditor(["name", "expression"])
        self.scrollLayout.addRow(self.state_variables_editor)
        # Coupling Variables
        self.scrollLayout.addRow(SubtitleLabel("Coupling Variables:"))
        self.coupling_variables_editor = BaseDynamicEditor(["name", "expression"])
        self.scrollLayout.addRow(self.coupling_variables_editor)
        # Transient Variables
        self.scrollLayout.addRow(SubtitleLabel("Transient Variables:"))
        self.transient_variables_editor = BaseDynamicEditor(["name", "expression"])
        self.scrollLayout.addRow(self.transient_variables_editor)
        # Parameters
        self.scrollLayout.addRow(SubtitleLabel("Parameters:"))
        self.parameters_editor = BaseDynamicEditor(["name", "value", "intro"])
        self.scrollLayout.addRow(self.parameters_editor)
        # References
        self.scrollLayout.addRow(SubtitleLabel("References:"))
        self.references_editor = BaseDynamicEditor(["detail"])
        self.scrollLayout.addRow(self.references_editor)
        # Create Btn
        self.finish_btn = PrimaryPushButton("Create")
        self.finish_btn.setFixedWidth(150)
        self.scrollLayout.addRow(self.finish_btn)
        self.vBoxLayout.addWidget(self.scrollArea)

    def set_format_data(self, dynamic: DynamicsModel):
        """拿到动力学模型中的数据，格式化之后回显到列表中

        Parameters
        ----------
        dynamic : DynamicsModel
            需要回显的动力学模型
        """
        self.dynamic_name_editor.setText(f"{dynamic.name}-copy")
        state_variables_data = []
        coupling_variables_data = []
        transient_variables_data = []
        parameters_data = []
        references_data = []

        for key in dynamic.state_variables:
            state_variables_data.append([key, dynamic.state_variables[key].expression])
        for key in dynamic.coupling_variables:
            coupling_variables_data.append(
                [key, dynamic.coupling_variables[key].expression]
            )
        for key in dynamic.transient_variables:
            transient_variables_data.append(
                [key, dynamic.transient_variables[key].expression]
            )
        for key in dynamic.parameters:
            parameters_data.append(
                [key, str(dynamic.parameters[key]), dynamic.docs[key]]
            )
        for item in dynamic.references:
            references_data.append([item])

        self.state_variables_editor.setValue(state_variables_data)
        self.coupling_variables_editor.setValue(coupling_variables_data)
        self.transient_variables_editor.setValue(transient_variables_data)
        self.parameters_editor.setValue(parameters_data)
        self.references_editor.setValue(references_data)

    def create_model(self):
        """点击 Create 按钮创建 新的动力学模型"""
        model_dict = {}
        model_dict["name"] = self.dynamic_name_editor.text().strip()
        name_flag = False
        if len(model_dict["name"]) == 0:
            show_error(
                "Please Name Your Model.",
                self._window,
            )
            return
        for dynamicsModel in self._workspace.dynamics:
            if dynamicsModel.name == model_dict["name"]:
                name_flag = True
                break
        if name_flag:
            show_error(
                "There is already a model with this name, please rename it",
                self._window,
            )
            return
        model_dict["state_variables"] = self.get_format_data(
            self.state_variables_editor.getValue(), "state_variables"
        )
        model_dict["coupling_variables"] = self.get_format_data(
            self.coupling_variables_editor.getValue(), "coupling_variables"
        )
        model_dict["transient_variables"] = self.get_format_data(
            self.transient_variables_editor.getValue(), "transient_variables"
        )
        parameters_data = self.get_format_data_parameters(
            self.parameters_editor.getValue()
        )
        if parameters_data[0] == "error":
            show_error(
                str(parameters_data[1]),
                self._window,
            )
            return
        model_dict["parameters"] = parameters_data[0]
        model_dict["docs"] = parameters_data[1]
        model_dict["references"] = self.references_editor.getValue()

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
        GLOBAL_SIGNAL.dynamicModelUpdate.emit(model_dict["name"], "create")

    def get_format_data(self, data, type=None) -> dict:
        """将表单收到的 state_variables coupling_variables
        transient_variables 数据格式化成与模板匹配的格式

        Parameters
        ----------
        data : array
            表单收集到的数据
        type : str, optional
            需要格式化的数据类型, by default None

        Returns
        -------
        dict
            返回一个字典
        """
        dict = {}
        if type == "state_variables":
            for item in data:
                if len(item) == 2 and len(item[0]) > 0 and len(item[1]) > 0:
                    dict.update({item[0]: StateVariable(expression=item[1])})
        if type == "coupling_variables":
            for item in data:
                if len(item) == 2 and len(item[0]) > 0 and len(item[1]) > 0:
                    dict.update({item[0]: CouplingVariable(expression=item[1])})
        if type == "transient_variables":
            for item in data:
                if len(item) == 2 and len(item[0]) > 0 and len(item[1]) > 0:
                    dict.update({item[0]: TransientVariable(expression=item[1])})
        return dict

    def get_format_data_parameters(self, data) -> list:
        """将变量、变量的值及变量的说明格式化成模板

        Parameters
        ----------
        data : list
            表单收到的数据

        Returns
        -------
        list
            返回一个列表
        """
        dict_parameters = {}
        dict_docs = {}
        for item in data:
            try:
                if len(item[1]) > 0:
                    dict_parameters[item[0]] = float(item[1])
                    dict_docs[item[0]] = item[2]
            except Exception as e:
                return ["error", e]
        return [dict_parameters, dict_docs]
