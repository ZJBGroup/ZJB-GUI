from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QWidget
from qfluentwidgets import (MessageBoxBase, SmoothScrollArea, TitleLabel,
                            TransparentPushButton)
from zjb.main.api import PSEResult, RegionalTimeSeries, SimulationResult

from ..panels.data_operation_panel import DataOperationPanel


class ChooseDataDialog(MessageBoxBase):
    """仿真结果、分析结果等包含多条数据的数据平铺、选择"""

    def __init__(self, data, project, parent=None):
        super().__init__(parent)
        self.data = data
        self.project = project
        self._setup_ui()

    def _setup_ui(self):
        self.yesButton.setText("Close")
        self.cancelButton.setText("Delete")
        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # self.formLayout.addRow(TitleLabel("Parameters:"))
        #
        # for parameter in self.data.parameters:
        #     btn_parameter = TransparentPushButton(f"{self.data.parameters[parameter]}")
        #     self.formLayout.addRow(BodyLabel(parameter), btn_parameter)

        self.formLayout.addRow(TitleLabel("Data:"))

        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setMinimumSize(750, 100)

        self.formLayout.addRow(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)

        self.scrollWidget = QWidget(self.scrollArea)

        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def _create_data_button(name, data):
            btn_data = TransparentPushButton(f"{name}")
            btn_data.clicked.connect(lambda: self._show_data_dialog(name, data))
            self.scrollLayout.addRow(btn_data)

        if isinstance(self.data, SimulationResult):
            for data in self.data.data:
                data_manipulation_panel = DataOperationPanel(
                    data._gid.str, data, self.project
                )
                self.scrollLayout.addRow(data_manipulation_panel)
        elif isinstance(self.data, PSEResult):
            for data in self.data.data:
                _create_data_button(data._gid.str, data)

        elif isinstance(self.data, RegionalTimeSeries):
            data_manipulation_panel = DataOperationPanel(
                str(self.data), self.data, self.project
            )
            self.scrollLayout.addRow(data_manipulation_panel)

        self.viewLayout.addLayout(self.formLayout)

    def _show_data_dialog(self, name, data):
        title = f"Data in {name}"
        content = """Select data for visualization or analysis."""
        w = ChooseDataDialog(data, self.project, self)
        w.exec()
