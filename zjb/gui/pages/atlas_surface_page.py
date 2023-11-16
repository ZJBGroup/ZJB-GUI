import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal
from pyqtgraph.opengl.shaders import FragmentShader, ShaderProgram, VertexShader
from qfluentwidgets import FluentIcon, Flyout, FlyoutAnimationType, InfoBarIcon

from zjb.main.api import Atlas, Subject, Surface, SurfaceRegionMapping

from .._rc import find_resource_file
from .atlas_surface_page_ui import Ui_atlas_surface_page
from .base_page import BasePage


class AtlasSurfacePage(BasePage):
    currentRegionClicked = pyqtSignal(int, list)

    def __init__(self, atlas: Atlas, subject: Subject):
        super().__init__(
            atlas._gid.str, atlas.name + " Surface Visualization", FluentIcon.EDUCATION
        )
        self.atlas = atlas
        self.subject = subject

        self._setup_ui()

        self.setObjectName(atlas._gid.str)

    def _setup_ui(self):
        self.ui = Ui_atlas_surface_page()
        self.ui.setupUi(self)

        self.ui.base_color_slider.setValue(75)
        self.ui.base_color_slider.setEnabled(False)

        self.ui.brain_regions_panel.region_signal_list.connect(
            self._on_region_signal_change
        )

        self._show_atlas()
        self._init_configure()

        self.currentRegionClicked.connect(self._3dbrain_region_clicked)

        self.ui.brain_regions_panel.show_tree_brain_regions(self.atlas)

    def _show_atlas(self):
        for data_key in self.subject.data:
            if isinstance(self.subject.data[data_key], Surface):
                self.surface = self.subject.data[data_key]
            elif isinstance(self.subject.data[data_key], SurfaceRegionMapping):
                self.surface_region_mapping = self.subject.data[data_key]

        self.ui.atlas_surface_view_widget.setAtlas(
            self.atlas, self.surface, self.surface_region_mapping
        )
        self.ui.atlas_surface_view_widget.setRegions(
            self.atlas, self.surface_region_mapping
        )

        self._on_color_number_changed("20")
        self._on_choose_colorbar_cbb_changed("default")

    def _init_configure(self):
        # colorbar选择
        self.list_of_maps_matplotlib = sorted(
            pg.colormap.listMaps("matplotlib"), key=lambda x: x.lower()
        )
        self.list_of_maps_colorcet = sorted(
            pg.colormap.listMaps("colorcet"), key=lambda x: x.lower()
        )

        # 颜色选择
        self.ui.choose_colorbar_cbb.clear()
        list_of_maps = self.list_of_maps_matplotlib + self.list_of_maps_colorcet
        self.ui.choose_colorbar_cbb.addItem("default")
        self.ui.choose_colorbar_cbb.addItem("BNA-standard")
        self.ui.choose_colorbar_cbb.addItems(list_of_maps)
        self.ui.choose_colorbar_cbb.currentTextChanged.connect(
            self._on_choose_colorbar_cbb_changed
        )

        self.ui.atlas_surface_view_widget.region_signal.connect(self._get_region)

        # 颜色数量选择
        self.ui.color_number_edit.textChanged.connect(self._on_color_number_changed)

        # 着色器选择
        self.ui.choose_shader_cbb.clear()
        list_of_shaders = [
            "ZJB special style",
            "balloon",
            "viewNormalColor",
            "normalColor",
            "shaded",
            "edgeHilight",
            "heightColor",
        ]
        self.ui.choose_shader_cbb.addItems(list_of_shaders)
        self.ui.choose_shader_cbb.currentTextChanged.connect(
            self._on_choose_shader_cbb_changed
        )

        # 底色选择
        self.ui.base_color_slider.valueChanged.connect(
            self._on_base_color_slider_changed
        )

        self.selectedRegions = []

    def _on_choose_colorbar_cbb_changed(self, colorbar_name):
        if colorbar_name == "BNA-standard":
            self.ui.atlas_surface_view_widget.setColorMap(
                "./" + find_resource_file("colorbar/BNA-standard.csv", abs=False)
            )
            self.ui.color_number_edit.setText("256")
        if colorbar_name == "default":
            self.ui.atlas_surface_view_widget.setColorMap("tab20", source="matplotlib")
        elif colorbar_name in self.list_of_maps_matplotlib:
            self.ui.atlas_surface_view_widget.setColorMap(
                colorbar_name, source="matplotlib"
            )
        elif colorbar_name in self.list_of_maps_colorcet:
            self.ui.atlas_surface_view_widget.setColorMap(
                colorbar_name, source="colorcet"
            )

    def _on_color_number_changed(self, color_number):
        if color_number.isnumeric() and int(color_number) > 0:
            color_number = int(color_number)
            if color_number > 10000:
                color_number = 9999
            self.regioncolor_list = list(np.linspace(0, 1, color_number)) * (
                int(self.atlas.number_of_regions / color_number) + 1
            )
            self.ui.atlas_surface_view_widget.setRegionColor(
                self.surface_region_mapping, self.regioncolor_list
            )
            self.regioncolor_list_contrast = self.regioncolor_list[:]
            self.base_color_value = self.ui.base_color_slider.value() / 100
            self.regioncolor_list_contrast = [
                self.base_color_value for _ in self.regioncolor_list_contrast
            ]
            # self.ui.base_color_slider.setEnabled(False)

    def _on_choose_shader_cbb_changed(self, shader_name):
        if shader_name == "ZJB special style":
            shader_program = ShaderProgram(
                "ZJBedgeLow",
                [
                    VertexShader(
                        """
                                varying vec3 normal;
                                void main() {
                                    // compute here for use in fragment shader
                                    normal = normalize(gl_NormalMatrix * gl_Normal);
                                    gl_FrontColor = gl_Color;
                                    gl_BackColor = gl_Color;
                                    gl_Position = ftransform();
                                }
                            """
                    ),
                    FragmentShader(
                        """
                                varying vec3 normal;
                                void main() {
                                    vec4 color = gl_Color;
                                    float s = pow(normal.x*normal.x + normal.y*normal.y, 2.0);
                                    color.x = color.x * (1. - s);
                                    color.y = color.y * (1. - s);
                                    color.z = color.z * (1. - s);
                                    gl_FragColor = color;
                                }
                            """
                    ),
                ],
            )
        else:
            shader_program = shader_name
        self.ui.atlas_surface_view_widget.setShader(shader_program)

    def _on_base_color_slider_changed(self):
        self.regioncolor_list_contrast = [
            self.ui.base_color_slider.value() / 100
            if i not in self.selectedRegions
            else n
            for i, n in enumerate(self.regioncolor_list_contrast)
        ]
        self.ui.atlas_surface_view_widget.setRegionColor(
            self.surface_region_mapping, self.regioncolor_list_contrast
        )
        self.base_color_value = self.ui.base_color_slider.value() / 100

    def _get_region(self, region_number):
        self.ui.base_color_slider.setEnabled(True)
        if region_number in self.selectedRegions:
            self.selectedRegions.remove(region_number)
        else:
            self.selectedRegions.append(region_number)
        regioncolor_array = np.full(
            len(self.regioncolor_list),
            self.ui.base_color_slider.value() / 100,
            dtype=float,
        )
        regioncolor_array[self.selectedRegions] = np.array(self.regioncolor_list)[
            self.selectedRegions
        ]
        self.regioncolor_list_contrast = list(regioncolor_array)
        self.ui.atlas_surface_view_widget.setRegionColor(
            self.surface_region_mapping, self.regioncolor_list_contrast
        )

        # 点击后传出信号：被选中的脑区
        self.currentRegionClicked.emit(region_number, self.selectedRegions)

    def _3dbrain_region_clicked(self, region_number, currentRegions):
        (
            region_data1,
            region_data2,
            region_data3,
        ) = self.ui.brain_regions_panel.ui.brain_regions_widget.set_region(
            region_number + 1
        )
        self.ui.brain_regions_panel.ui.brain_regions_widget.set_regions(currentRegions)
        if region_data1 != 0:
            content = (
                "No."
                + str(region_number + 1)
                + "  brain region is currently checked"
                + "\n"
                "Region name："
                + region_data1
                + "\n"
                + "Subregion name："
                + region_data2
                + "\n"
                + "Anatomic profile："
                + region_data3
            )
        Flyout.create(
            icon=InfoBarIcon.INFORMATION,
            title="脑区信息",
            content=content,
            target=self.ui.atlas_surface_view_widget,
            isClosable=True,
            aniType=FlyoutAnimationType.DROP_DOWN,
            parent=self,
        )

    def _on_region_signal_change(self, number_list_regions):
        self.select_regions(number_list_regions)

    def select_regions(self, number_list_regions):
        self.selectedRegions = number_list_regions
        self.ui.base_color_slider.setEnabled(True)
        if hasattr(self, "regioncolor_list"):
            regioncolor_array = np.full(
                len(self.regioncolor_list),
                self.ui.base_color_slider.value() / 100,
                dtype=float,
            )
            regioncolor_array[self.selectedRegions] = np.array(self.regioncolor_list)[
                self.selectedRegions
            ]
            self.regioncolor_list_contrast = list(regioncolor_array)
            self.ui.atlas_surface_view_widget.setRegionColor(
                self.surface_region_mapping, self.regioncolor_list_contrast
            )
