from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    FluentIcon,
    IconWidget,
    LineEdit,
    MessageBoxBase,
    PrimaryPushButton,
    SubtitleLabel,
    TitleLabel,
)

from zjb.main.api import Project, RegionalConnectivity, RegionSpace, Subject

from .._global import get_workspace
from ..common.utils import show_error
from ..panels.data_dict_panel import SubjectDataDictPanel
from ..widgets.file_editor import OpenFileEditor
from .base_page import BasePage


class SubjectPage(BasePage):
    def __init__(self, subject: Subject, project: Project):
        super().__init__(subject._gid.str, subject.name, FluentIcon.PEOPLE)
        self._subject = subject
        self._project = project

        self._workspace = get_workspace()
        self._setup_ui()

        self._subject.observe(self.updata_list, "data")

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 页面信息部分
        self.info_panel = QWidget(self)
        self.info_panel_layout = QHBoxLayout(self.info_panel)
        self.info_panel_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.pageicon = IconWidget(FluentIcon.PEOPLE, self)
        self.pageicon.setFixedSize(140, 140)
        self.info_panel_layout.addWidget(self.pageicon)

        # 信息部分右侧文字及按钮部分
        self.detail_panel = QWidget(self)
        self.detail_panel.setMinimumHeight(40)
        self.detail_panel_layout = QVBoxLayout(self.detail_panel)
        self.detail_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detail_panel_layout.setContentsMargins(30, 0, 0, 0)
        self.detail_panel_layout.addWidget(TitleLabel(self._subject.name))
        self.detail_panel_layout.addWidget(BodyLabel("info: ..."))

        # 按钮组
        self.button_group = QWidget(self)
        self.button_group_layout = QHBoxLayout(self.button_group)
        self.button_group_layout.setContentsMargins(0, 25, 0, 0)
        self.btn_import_connectivity = PrimaryPushButton("Import Connectivity")
        self.btn_import_connectivity.clicked.connect(self._import_connectivity)
        self.button_group_layout.addWidget(self.btn_import_connectivity)

        # for name, data in self.subject.data.items():
        #     data_manipulation_panel = DataOperationPanel(name, data, self.project)
        #     self.formLayout.addRow(data_manipulation_panel)
        self.detail_panel_layout.addWidget(self.button_group)
        self.info_panel_layout.addWidget(self.detail_panel)
        self.vBoxLayout.addWidget(self.info_panel)

        self.vBoxLayout.addWidget(SubtitleLabel(f"Data in {self._subject.name}:"))
        # 数据列表
        self.data_list = SubjectDataDictPanel(self._subject, self._project, self)
        self.vBoxLayout.addWidget(self.data_list)

    def _import_connectivity(self):
        """导入连接的 方法"""
        dialog = ImportConnectivityDialog(self.window())
        if dialog.exec():
            name = dialog.edit_text.text()
            if not name:
                show_error("The name of the data cannot be empty", self.window())
                return
            connectivity = RegionalConnectivity.from_npy(
                dialog.file_eidtor.text(), dialog.current_space
            )
            self._subject.data |= {name: connectivity}

    def updata_list(self, event):
        """添加新的数据以后，调用方法更新数据列表

        Parameters:
        ----------
        event:
            `subject.data`变化的事件
        """
        self.data_list.data = event.new


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
