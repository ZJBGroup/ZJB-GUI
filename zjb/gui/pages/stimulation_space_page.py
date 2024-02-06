import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from qfluentwidgets import FluentIcon

from zjb.gui.panels.stimulation_brain_tree_panel import StimulationBrainTreePanel
from zjb.gui.panels.stimulation_value_panel import StimulationValuePanel
from zjb.main.api import Atlas, Subject, Surface, SurfaceRegionMapping
from zjb.main.visualization.surface_space import AtlasSurfaceViewWidget

from .._global import GLOBAL_SIGNAL
from .._rc import find_resource_file
from .base_page import BasePage

# import pyqtgraph as pg
# import pyqtgraph.opengl as gl


def format_value(val: float):
    return val / 2 + 0.5


class StimulationSpacePage(BasePage):
    currentRegionClicked = pyqtSignal(int)

    def __init__(self, atlas: Atlas, subject: Subject):
        super().__init__("stimulation_space", "stimulation_space", FluentIcon.EDUCATION)
        self.atlas = atlas
        self.subject = subject
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("stimulation_space")
        self.resize(847, 551)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        # 树形列表
        self.brain_regions_tree = StimulationBrainTreePanel(self)
        self.brain_regions_tree.setObjectName("brain_regions_tree")
        self.horizontalLayout_3.addWidget(self.brain_regions_tree)
        # 脑区立体图
        self.stimulation_space_view_widget = AtlasSurfaceViewWidget()
        self.horizontalLayout_3.addWidget(self.stimulation_space_view_widget)
        # 右侧列表
        self.value_panel = StimulationValuePanel(self)
        self.value_panel.setObjectName("value_panel")
        self.horizontalLayout_3.addWidget(self.value_panel)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self._show_atlas()
        self.brain_regions_tree.show_tree_brain_regions(self.atlas)

        self.stimulation_space_view_widget.region_signal.connect(self._click_region)
        self.brain_regions_tree.brain_regions_widget.clickedRegionSignal.connect(
            self._tree_clicked
        )
        self.value_panel.value_editor_widget.addStimulationValueSignal.connect(
            self.addValueToView
        )
        self.value_panel.value_list_widget.deleteViewValueSignal.connect(
            self.deleteViewValue
        )
        self.value_panel.create_btn.clicked.connect(self.create_stimulation_space)

    def create_stimulation_space(self):
        """点击 create 按钮，创建刺激的空间分布"""
        GLOBAL_SIGNAL.stimulationSpaceCreated.emit(
            self.getRouteKey(), self.regioncolor_list
        )

    def deleteViewValue(self, region_num):
        """删除值以后同步到3D脑图中

        Parameters
        ----------
        region_num : str
            脑区编号
        """
        self.regioncolor_list[int(region_num) - 1] = self.default_regioncolor_list[
            int(region_num) - 1
        ]
        _setregioncolor = [format_value(item) for item in self.regioncolor_list]
        self.stimulation_space_view_widget.setRegionColor(
            self.surface_region_mapping, _setregioncolor
        )

    def addValueToView(self, list):
        """添加值以后，同步到3D脑图中

        Parameters
        ----------
        list : list
            脑区值列表
            data_list[0] brain num
            data_list[4] stimulation value
        """
        self.regioncolor_list[int(list[0]) - 1] = float(list[4])
        _setregioncolor = [format_value(item) for item in self.regioncolor_list]
        self.stimulation_space_view_widget.setRegionColor(
            self.surface_region_mapping, _setregioncolor
        )

    def _tree_clicked(self, data_list: list):
        """点击左侧的列表，在右侧的面板中显示指定脑区信息

        Parameters
        ----------
        data_list : list
            所点击条目的脑区信息
            data_list[0] anat-profile
            data_list[1] subregion
            data_list[2] region
            data_list[3] brain num
        """
        data_list.reverse()
        self.value_panel.value_editor_widget.setValue(data_list)

    def _show_atlas(self):
        """初始化3D脑图谱"""
        for data_key in self.subject.data:
            if isinstance(self.subject.data[data_key], Surface):
                self.surface = self.subject.data[data_key]
            elif isinstance(self.subject.data[data_key], SurfaceRegionMapping):
                self.surface_region_mapping = self.subject.data[data_key]
        self.stimulation_space_view_widget.setAtlas(
            self.atlas, self.surface, self.surface_region_mapping
        )
        self.stimulation_space_view_widget.setRegions(
            self.atlas, self.surface_region_mapping
        )
        # 初始化3D脑区图案
        self.default_regioncolor_list = np.full(
            self.atlas.number_of_regions,
            0,
            dtype=float,
        )
        self.regioncolor_list = [item for item in self.default_regioncolor_list]
        _setregioncolor = [format_value(item) for item in self.regioncolor_list]
        self.stimulation_space_view_widget.setRegionColor(
            self.surface_region_mapping, _setregioncolor
        )
        self.stimulation_space_view_widget.setColorMap(
            "./" + find_resource_file("colorbar/CET-ZJB.csv", abs=False)
        )
        # self.legendLabels = np.linspace(1.0, -1.0, 5)
        # self.legendPos = np.linspace(1, 0, 5)
        # self.legend = dict(
        #     zip(map(str, np.around(self.legendLabels, 2)), self.legendPos)
        # )
        # self.gll = gl.GLGradientLegendItem(
        #     pos=(10, 10),
        #     size=(20, 120),
        #     gradient=self.stimulation_space_view_widget.color_map,
        #     labels=self.legend,
        # )
        # self.stimulation_space_view_widget.addItem(self.gll)

    def _click_region(self, region_number):
        """点击3D图脑区的槽函数

        Parameters
        ----------
        region_number : int
            脑区编号
        """
        self.brain_regions_tree.brain_regions_widget.set_region(region_number + 1)
