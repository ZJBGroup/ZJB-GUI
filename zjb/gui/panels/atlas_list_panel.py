# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem, QVBoxLayout
from qfluentwidgets import (
    ComboBox,
    FluentIcon,
    InfoBarIcon,
    ListWidget,
    MessageBox,
    MessageDialog,
    PushButton,
    ScrollArea,
    SubtitleLabel,
    TeachingTip,
    TeachingTipTailPosition,
    TeachingTipView,
)

from zjb.gui._global import GLOBAL_SIGNAL, get_workspace
from zjb.gui.common.utils import show_error
from zjb.gui.pages.atlas_surface_page import Atlas_Surface_Page
from zjb.main.manager.workspace import Workspace


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
                atlasItem.setIcon(FluentIcon.DOCUMENT.icon())

                self.listWidget.addItem(atlasItem)

    def _itemClicked(self, item):
        self.select_atlas_name = item.text()
        for atlas in self._workspace.atlases:
            if atlas.name == self.select_atlas_name:
                select_atlas = atlas
                break

        for subject in self._workspace.subjects:
            if subject.name == "fsaverage":
                select_subject = subject
                break

        GLOBAL_SIGNAL.requestAddPage.emit(
            Atlas_Surface_Page(
                select_atlas.name,
                select_atlas.name + " Surface Visualization",
                FluentIcon.DOCUMENT,
                select_atlas,
                select_subject,
            )
        )

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