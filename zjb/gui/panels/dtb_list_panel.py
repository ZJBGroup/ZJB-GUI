# coding:utf-8

from PyQt5.QtWidgets import QTreeWidgetItem
from qfluentwidgets import FluentIcon, ScrollArea, SubtitleLabel, TreeWidget, VBoxLayout

from zjb.main.api import DTB, DTBModel, Project, Subject, Workspace

from .._global import GLOBAL_SIGNAL
from ..pages.dtb_model_page import DTBModelPage
from ..pages.dtb_page import DTBPage
from ..pages.subject_page import SubjectPage


class DTBInterface(ScrollArea):
    """DTBInterface 树形结构"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DTBInterface")
        self.setStyleSheet("#DTBInterface{background:transparent;border:none}")

        self.vBoxLayout = VBoxLayout(self)
        self._set_placeholder()

        GLOBAL_SIGNAL.workspaceChanged.connect(self._on_no_workspace)
        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(self._on_workspace)

        print(GLOBAL_SIGNAL)

    def _set_placeholder(self):
        label = SubtitleLabel("You have not yet opened a workspace.")
        label.setWordWrap(True)
        self.vBoxLayout.addWidget(label)

    def _clear_layout(self):
        for widget in reversed(self.vBoxLayout.widgets):
            self.vBoxLayout.deleteWidget(widget)

    def _on_no_workspace(self):
        self._clear_layout()

        self._set_placeholder()

    def _on_workspace(self, ws: Workspace):
        self._clear_layout()

        self.tree = TreeWidget(self)
        self.vBoxLayout.addWidget(self.tree)
        ProjectItem(ws, self.tree)

        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_click)

    def _on_item_click(self, item):
        if isinstance(item, SubjectItem):
            GLOBAL_SIGNAL.requestAddPage.emit(
                item.subject._gid.str, lambda _: SubjectPage(item.subject)
            )
            return
        if isinstance(item, DTBItem):
            GLOBAL_SIGNAL.requestAddPage.emit(
                item.dtb._gid.str, lambda _: DTBPage(item.dtb)
            )
            return
        if isinstance(item, DTBModelItem):
            GLOBAL_SIGNAL.requestAddPage.emit(
                item.model._gid.str, lambda _: DTBModelPage(item.model)
            )
            return


class ProjectItem(QTreeWidgetItem):
    def __init__(self, project: Project, parent):
        super().__init__(parent)

        self.project = project

        self.setText(0, project.name)
        self.setIcon(0, FluentIcon.FOLDER.icon())
        for child in project.children:
            _ = ProjectItem(child, self)
        for subject in project.subjects:
            _ = SubjectItem(subject, self)
        for model in project.models:
            _ = DTBModelItem(model, self)
        for dtb in project.dtbs:
            _ = DTBItem(dtb, self)


class SubjectItem(QTreeWidgetItem):
    def __init__(self, subject: Subject, parent):
        super().__init__(parent)
        self.subject = subject

        self.setText(0, subject.name)
        self.setIcon(0, FluentIcon.PEOPLE.icon())


class DTBModelItem(QTreeWidgetItem):
    def __init__(self, model: DTBModel, parent):
        super().__init__(parent)

        self.model = model

        self.setText(0, model.name)
        self.setIcon(0, FluentIcon.IOT.icon())


class DTBItem(QTreeWidgetItem):
    def __init__(self, dtb: DTB, parent):
        super().__init__(parent)

        self.dtb = dtb

        self.setText(0, dtb.name)
        self.setIcon(0, FluentIcon.ALBUM.icon())
