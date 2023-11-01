# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractScrollArea, QComboBox, QTreeWidgetItem
from qfluentwidgets import FluentIcon, ScrollArea, SubtitleLabel, TreeWidget, VBoxLayout
from zjb.dos.data import Data
from zjb.main.api import DTB, DTBModel, Project, Subject, Workspace

from .._global import GLOBAL_SIGNAL, get_workspace
from ..pages.dtb_model_page import DTBModelPage
from ..pages.dtb_page import DTBPage
from ..pages.subject_page import SubjectPage
from ..widgets.new_entity_menu import NewEntityMenu


class DTBInterface(ScrollArea):
    """DTBInterface 树形结构"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DTBInterface")
        self.setStyleSheet("#DTBInterface{background:transparent;border:none}")
        self.rightClickItem = None
        self.vBoxLayout = VBoxLayout(self)
        self._set_placeholder()

        GLOBAL_SIGNAL.workspaceChanged.connect(self._on_no_workspace)
        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(self._on_workspace)
        GLOBAL_SIGNAL.dtbListUpdate.connect(self._update_tree)
        print(GLOBAL_SIGNAL)

    def _update_tree(self, new_entity):
        """创建新的实体之后会更新列表"""
        if isinstance(new_entity, Project):
            new_item = ProjectItem(new_entity, self.rightClickItem)
            self.tree.scrollToItem(new_item)
            self.tree.setCurrentItem(new_item)

        if isinstance(new_entity, Subject):
            new_item = SubjectItem(new_entity, self.rightClickItem)
            self.tree.scrollToItem(new_item)
            self.tree.setCurrentItem(new_item)

        if isinstance(new_entity, DTBModel):
            new_item = DTBModelItem(new_entity, self.rightClickItem)
            self.tree.scrollToItem(new_item)
            self.tree.setCurrentItem(new_item)

        if isinstance(new_entity, DTB):
            new_item = DTBItem(new_entity, self.rightClickItem)
            self.tree.scrollToItem(new_item)
            self.tree.setCurrentItem(new_item)

    def _set_placeholder(self):
        """还未打开工作空间的时候展示提示文案"""
        label = SubtitleLabel("You have not yet opened a workspace.")
        label.setWordWrap(True)
        self.vBoxLayout.addWidget(label)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

    def _clear_layout(self):
        """清空布局"""
        for widget in reversed(self.vBoxLayout.widgets):
            self.vBoxLayout.deleteWidget(widget)

    def _on_no_workspace(self):
        """没有工作空间的时候清空布局、设置提示文案"""
        self._clear_layout()
        self._set_placeholder()

    def _on_workspace(self, ws: Workspace):
        """打开工作空间根据数据配置列表"""
        self._clear_layout()
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.tree = TreeWidget(self)
        self.vBoxLayout.addWidget(self.tree)
        ProjectItem(ws, self.tree)

        self.tree.setHeaderHidden(True)
        # self.tree.expandAll()
        self.tree.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )

        self.tree.itemClicked.connect(self._on_item_click)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

    def _on_item_click(self, item):
        """左键点击一个条目"""
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

    def _show_context_menu(self, pos):
        """右键点击一个条目时，触发右键菜单"""
        self.rightClickItem = self.tree.itemAt(pos)
        self.tree.setCurrentItem(self.rightClickItem)
        rightMenu = NewEntityMenu(
            item=self.rightClickItem.getData(), window=self.window()
        )
        rightMenu.exec(self.tree.mapToGlobal(pos))


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

    def getData(self):
        return self.project


class SubjectItem(QTreeWidgetItem):
    def __init__(self, subject: Subject, parent):
        super().__init__(parent)
        self.subject = subject

        self.setText(0, subject.name)
        self.setIcon(0, FluentIcon.PEOPLE.icon())

    def getData(self):
        return self.subject


class DTBModelItem(QTreeWidgetItem):
    def __init__(self, model: DTBModel, parent):
        super().__init__(parent)

        self.model = model

        self.setText(0, model.name)
        self.setIcon(0, FluentIcon.IOT.icon())

    def getData(self):
        return self.model


class DTBItem(QTreeWidgetItem):
    def __init__(self, dtb: DTB, parent):
        super().__init__(parent)

        self.dtb = dtb

        self.setText(0, dtb.name)
        self.setIcon(0, FluentIcon.ALBUM.icon())

    def getData(self):
        return self.dtb
