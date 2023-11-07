from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QFormLayout, QVBoxLayout
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    FluentIcon,
    LineEdit,
    MessageBoxBase,
    PrimaryPushButton,
    SubtitleLabel,
    TitleLabel,
)

from zjb.main.api import RegionalConnectivity, RegionSpace, Subject

from .._global import get_workspace
from ..common.utils import show_error
from ..panels.data_operation_panel import DataOperationPanel
from ..widgets.file_editor import OpenFileEditor
from .base_page import BasePage


class SubjectPage(BasePage):
    def __init__(self, subject: Subject):
        super().__init__(subject._gid.str, subject.name, FluentIcon.PEOPLE)
        self.subject = subject

        self._setup_ui()

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.vBoxLayout.addWidget(TitleLabel("Subject"))
        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.addLayout(self.formLayout)

        self.formLayout.addRow(BodyLabel("name:"), BodyLabel(self.subject.name))
        self.formLayout.addRow(BodyLabel("info:"), BodyLabel("..."))

        self.btn_import_connectivity = PrimaryPushButton("Import Connectivity")
        self.btn_import_connectivity.clicked.connect(self._import_connectivity)
        self.vBoxLayout.addWidget(self.btn_import_connectivity)

        for name, data in self.subject.data.items():
            data_manipulation_panel = DataOperationPanel(name, data)
            self.formLayout.addRow(data_manipulation_panel)

    def _import_connectivity(self):
        dialog = ImportConnectivityDialog(self)
        if dialog.exec():
            name = dialog.edit_text.text()
            if not name:
                show_error("The name of the data cannot be empty", self.window())
                return
            connectivity = RegionalConnectivity.from_npy(
                dialog.file_eidtor.text(), dialog.current_space
            )
            self.subject.data |= {name: connectivity}


class ImportConnectivityDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.viewLayout.addWidget(SubtitleLabel("Import Connectivity"))
        self.formLayout = QFormLayout()
        self.viewLayout.addLayout(self.formLayout)

        self.edit_text = LineEdit()
        self.edit_text.setPlaceholderText("Input name here")
        self.formLayout.addRow(BodyLabel("Name:"), self.edit_text)

        self.file_eidtor = OpenFileEditor(filter="Numpy Array (*.npy)")
        self.formLayout.addRow(BodyLabel("File:"), self.file_eidtor)

        self.combo = ComboBox()
        self.formLayout.addRow(BodyLabel("Atlas:"), self.combo)

        ws = get_workspace()
        assert ws
        for atlas in ws.atlases:
            self.combo.addItem(atlas.name, userData=atlas.space)

    @property
    def current_space(self) -> RegionSpace:
        return self.combo.currentData()  # type: ignore
