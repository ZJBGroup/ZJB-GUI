import numpy as np
import pyqtgraph.opengl as gl
from PyQt5 import QtCore
from qfluentwidgets import FluentIcon
import sip

from zjb.main.api import Atlas, RegionalTimeSeries, Subject, Surface, SurfaceRegionMapping

from .._global import GLOBAL_SIGNAL
from .._rc import find_resource_file
from .base_page import BasePage
from .time_series_page_ui import Ui_time_series_page


class RegionalTimeSeriesPage(BasePage):
    def __init__(self, regional_timeseries: RegionalTimeSeries, subject: Subject):
        super().__init__(regional_timeseries._gid.str + "Visualization", "Time Series", FluentIcon.SPEED_HIGH)
        self.timeseries = regional_timeseries
        self.atlas = regional_timeseries.space.atlas
        self.subject = subject
        self.list_selected_regions = None

        self._setup_ui()
        self.setObjectName(regional_timeseries._gid.str + "Visualization")

    def _setup_ui(self):
        self.ui = Ui_time_series_page()
        self.ui.setupUi(self)

        self.ui.time_edit.setMinimumSize(160, 20)
        self._set_time_series()
        self._show_atlas()
        self.ui.brain_regions_panel.region_signal_list.connect(
            self._on_region_signal_change
        )
        self.ui.brain_regions_panel.show_tree_brain_regions(self.atlas)

        self.ui.speed_slider.setValue(0)
        self.ui.speed_slider.valueChanged.connect(self._on_speed_slider_changed)

        self.ui.update_btn.clicked.connect(self._on_update_btn_clicked)

        self.ui.time_slider.valueChanged.connect(self._on_time_slider_changed)
        
        self.ui.start_btn.setChecked(True)
        self.ui.start_btn.clicked.connect(self._on_start_btn_clicked)

    def _show_atlas(self):
        for data_key in self.subject.data:
            if isinstance(self.subject.data[data_key], Surface):
                self.surface = self.subject.data[data_key]
            elif isinstance(self.subject.data[data_key], SurfaceRegionMapping):
                self.surface_region_mapping = self.subject.data[data_key]
        self.ui.atlas_surface_view_widget.clear()
        self.ui.atlas_surface_view_widget.setAtlas(
            self.atlas, self.surface, self.surface_region_mapping
        )
        self.ui.atlas_surface_view_widget.setColorMap(
            "./" + find_resource_file("colorbar/CET-ZJB.csv", abs=False)
        )
        self.ui.time_slider.setValue(0)
        self.setColorBar()
        self._update()

    def _set_time_series(self):
        (self.max_time, self.num_brainregion) = self.timeseries.data.shape
        self.ui.time_slider.setMaximum(self.max_time)
        self.ui.up_color_edit.setText(str(round(self.timeseries.data.max(), 2)))
        self.ui.low_color_edit.setText(str(round(self.timeseries.data.min(), 2)))
        self.colorbar_max = float(self.ui.up_color_edit.text())
        self.colorbar_min = float(self.ui.low_color_edit.text())
        self.ui.speed_slider.setValue(0)
        self.ui.start_btn.setText("Start")
        self.ui.start_btn.setChecked(True)
        self.ui.time_series_widget.setTimeSeries(self.timeseries)

    def setColorBar(self):
        self.colorbar_max = float(self.ui.up_color_edit.text())
        self.colorbar_min = float(self.ui.low_color_edit.text())
        # self._update()
        self.legendLabels = np.linspace(self.colorbar_max, self.colorbar_min, 5)
        self.legendPos = np.linspace(1, 0, 5)
        self.legend = dict(
            zip(map(str, np.around(self.legendLabels, 2)), self.legendPos)
        )
        self.gll = gl.GLGradientLegendItem(
            pos=(10, 10),
            size=(20, 120),
            gradient=self.ui.atlas_surface_view_widget.color_map,
            labels=self.legend,
        )
        self.ui.atlas_surface_view_widget.addItem(self.gll)

    def _on_speed_slider_changed(self):
        if 0 <= self.time < self.max_time - self.ui.speed_slider.value():
            self.time += self.ui.speed_slider.value()
        self.ui.time_slider.setMaximum(
            self.max_time - self.ui.speed_slider.value()
        )  # 避免运行时超出时间轴阈值
        if self.ui.start_btn.isChecked():
            self.ui.start_btn.setText("Pause")
            self.timer.start(300)
            self.ui.start_btn.setChecked(False)
        else:
            pass

    def _on_time_slider_changed(self):
        self.time = self.ui.time_slider.value()
        if self.ui.speed_slider.value() > 0:
            self.timer.start(300)

    def _on_update_btn_clicked(self):
        self.ui.atlas_surface_view_widget.removeItem(self.gll)
        self.setColorBar()

    def _on_start_btn_clicked(self):
        if self.ui.start_btn.isChecked():
            self.ui.speed_slider.setValue(0)
            self.ui.start_btn.setText("Start")
            self.ui.start_btn.setChecked(True)
            self.timer.stop()
        else:
            self.ui.start_btn.setText("Pause")
            self.ui.speed_slider.setValue(10)
            self.timer.start(300)
            self.ui.start_btn.setChecked(False)

    def _update(self):
        self.time = self.ui.time_slider.value()
        #
        # if self.list_selected_regions is not None:
        self.selected_timeseries_data = np.zeros(self.timeseries.data.shape)
        self.selected_timeseries_data[
            :, self.list_selected_regions
        ] = self.timeseries.data[:, self.list_selected_regions]

        def _time_update():
            if sip.isdeleted(self):
                self.timer.stop()
            else:
                regionColor = (
                    self.selected_timeseries_data[self.time] - self.colorbar_min
                ) / (self.colorbar_max - self.colorbar_min)
                self.ui.atlas_surface_view_widget.ampl = np.array(regionColor)[
                    self.ui.atlas_surface_view_widget.labels
                ]
                colors = self.ui.atlas_surface_view_widget.color_map.map(
                    self.ui.atlas_surface_view_widget.ampl, mode="float"
                )
                colors[
                    self.selected_timeseries_data[
                        self.time, np.squeeze(self.ui.atlas_surface_view_widget.labels)
                    ]
                    == 0,
                    :,
                ] = [0.7, 0.7, 0.7, 1]
                self.ui.atlas_surface_view_widget.md.setVertexColors(colors)
                self.ui.atlas_surface_view_widget.surface.vertexes = None
                self.ui.atlas_surface_view_widget.surface.update()

                self.ui.time_slider.setValue(self.time)
                self.ui.time_edit.setText(
                    str(round(self.timeseries.time[self.time], 4)) + self.timeseries.sample_unit.value
                )  # 保留4位小数

                if 0 <= self.time < self.max_time - self.ui.speed_slider.value():
                    self.time += self.ui.speed_slider.value()
                else:
                    self.timer.stop()
                    self.ui.speed_slider.setValue(0)
                    self.ui.start_btn.setText("Start")
                    self.ui.start_btn.setChecked(True)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(_time_update)

    def _on_region_signal_change(self, number_list_regions):
        self.select_regions(number_list_regions)

    def select_regions(self, selected_regions):
        self.ui.time_series_widget.setSelectRegion(selected_regions)
        self.list_selected_regions = selected_regions

        if self.list_selected_regions is not None and self.timeseries is not None:
            self.selected_timeseries_data = np.zeros(self.timeseries.data.shape)
            self.selected_timeseries_data[
                :, self.list_selected_regions
            ] = self.timeseries.data[:, self.list_selected_regions]

    def closeEvent(self, event):
    # 停止定时器
        self.timer.stop()
