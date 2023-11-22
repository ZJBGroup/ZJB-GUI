from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QListWidgetItem, QVBoxLayout
from qfluentwidgets import FluentIcon, ListWidget, ScrollArea
from qfluentwidgets.common.icon import FluentIconEngine, Icon
from zjb.main.manager.workspace import Workspace

from .._global import GLOBAL_SIGNAL, get_workspace
from ..common.utils import show_error
from ..pages.atlas_surface_page import AtlasSurfacePage
from ..pages.base_page import BasePage


class AtlasInterface(ScrollArea):
    """AtlasInterface 目录列表"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.listWidget = ListWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.listWidget)
        self.setObjectName("AtlasInterface")
        self.setStyleSheet("#AtlasInterface{background:transparent;border:none}")
        self.listWidget.itemClicked.connect(self._itemClicked)
        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(self._sync_atlas)

    def _sync_atlas(self):
        self.listWidget.clear()
        self._workspace = get_workspace()
        if not self._workspace:
            show_error("Please 'Open' or 'New' a workspace first", self.window())
        else:
            for atlas in self._workspace.atlases:
                atlasItem = QListWidgetItem(atlas.name)
                atlasItem.setIcon(QIcon(FluentIconEngine(Icon(FluentIcon.EDUCATION))))

                self.listWidget.addItem(atlasItem)

    def setWorkspace(self, workspace: Workspace):
        """设置工作空间"""
        self._workspace = workspace

    def _itemClicked(self, item: QListWidgetItem):
        select_atlas_name = item.text()
        for atlas in self._workspace.atlases:
            if atlas.name == select_atlas_name:
                select_atlas = atlas
                break

        for subject in self._workspace.subjects:
            if select_atlas_name == "AAL90":
                if subject.name == "cortex_80k":
                    select_subject = subject
                    break
            else:
                if subject.name == "fsaverage":
                    select_subject = subject
                    break

        GLOBAL_SIGNAL.requestAddPage.emit(
            select_atlas._gid.str,
            lambda _: AtlasSurfacePage(select_atlas, select_subject),
        )

    #
    # def _addpage(self, routeKey: str) -> BasePage:
    #     _page = AtlasSurfacePage(
    #         routeKey,
    #         self.select_atlas.name + " Surface Visualization",
    #         FluentIcon.DOCUMENT,
    #         self.select_atlas,
    #         self.select_subject,
    #     )
    #     return _page

    # GLOBAL_SIGNAL.requestAddPage.emit(
    #     Atlas_Surface_Page(
    #         select_atlas.name,
    #         select_atlas.name + " Surface Visualization",
    #         FluentIcon.DOCUMENT,
    #         select_atlas,
    #         select_subject,
    #     )
    # )

    # def showTip(self, widget):
    #     position = TeachingTipTailPosition.BOTTOM
    #     view = TeachingTipView(
    #         icon=InfoBarIcon.SUCCESS,
    #         title='Add subject',
    #         content="Please select the appropriate subjects to display individualized cortical surface and brain atlase",
    #         isClosable=True,
    #         tailPosition=position,
    #         parent=self
    #     )
    #     # add widget to view
    #     self.combo_box = ComboBox()
    #     # self.combo_box.setText('Select Subjects')
    #     item = []
    #     self.combo_box.setFixedWidth(120)
    #     for subject in self._workspace.subjects:
    #         item.append(subject.name)
    #     self.combo_box.addItems(item)
    #     view.addWidget(self.combo_box, align=Qt.AlignLeft)
    #     button = PushButton('ok')
    #     button.setFixedWidth(120)
    #     button.clicked.connect(self._on_ok_clicked)
    #     button.clicked.connect(view.closed)
    #     view.addWidget(button, align=Qt.AlignRight)
    #     w = TeachingTip.make(
    #         target=widget,
    #         view=view,
    #         duration=-1,
    #         tailPosition=position,
    #         parent=self
    #     )
    #     view.closed.connect(w.close)

    # def _on_ok_clicked(self):
    #     for atlas in self._workspace.atlases:
    #         if atlas.name == self.select_atlas_name:
    #             select_atlas = atlas
    #             break
    #
    #     for subject in self._workspace.subjects:
    #         if subject.name == self.combo_box.text():
    #             select_subject = subject
    #             break
    #
    #     GLOBAL_SIGNAL.requestAddPage.emit(
    #         Atlas_Surface_Page("Atlas", "Atlas", FluentIcon.DOCUMENT, select_atlas, select_subject)
    #     )
    #
