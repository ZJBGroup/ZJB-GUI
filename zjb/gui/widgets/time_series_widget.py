import random
import typing

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPen
from QCustomPlot_PyQt5 import *

from zjb.main.api import TimeSeries

TimeSeriesOrNone = typing.Optional[TimeSeries]


class TimeSeriesWidget(QCustomPlot):
    _time_series: TimeSeriesOrNone

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setInteractions(
            QCP.Interaction.iRangeDrag
            | QCP.Interaction.iRangeZoom
            | QCP.Interaction.iSelectAxes
            | QCP.Interaction.iSelectLegend
            | QCP.Interaction.iSelectPlottables
        )  # 图像的缩放
        self.setInteractions(
            QCP.Interaction.iRangeDrag
            | QCP.Interaction.iRangeZoom
            | QCP.Interaction.iSelectAxes
            | QCP.Interaction.iSelectLegend
            | QCP.Interaction.iSelectPlottables
        )  # 图像的缩放

        self.xAxis.setLabel("time(ms)")
        # self.yAxis.setLabel("amplitude")  # xy轴的标注
        self.yAxis.setTickLabels(False)  # 不显示y轴数值
        self.plotLayout().insertRow(0)
        self.title = QCPTextElement(
            self, "TimeSeries", QFont("sans", 15, QFont.Weight.Bold)
        )  # 图的大标题
        self.plotLayout().addElement(0, 0, self.title)
        self._time_series = None
        self.list_br = None

    def setTimeSeries(self, time_series: TimeSeriesOrNone):
        """设置要可视化的时间序列"""
        self._time_series = time_series
        if isinstance(self.list_br, list):
            self._update()

    def setSelectRegion(self, number_br):
        """被选择的脑区"""
        self.list_br = number_br
        if self._time_series is not None:
            self._update()  # 画选中脑区的时间序列

    def _update(self):
        if self.list_br != None:
            self.timeseries_data = (
                self._time_series.data
            )  # data: array[float], 时空序列数据,第一维固定为时间（时刻）数据，其中“：”为维度>=1的空间维度
            self.time_ticks = (
                self._time_series.time
            )  # time = Array[float] 时间（时刻）维度，即时间值数组
            self.sample_unit = (
                self._time_series.sample_unit
            )  # sample_unit: 采样单位，时间维度，ms，s等
            self.start_time = self._time_series.start_time  # start_time: float 开始的时刻
            # self.br_names = self._time_series.atlas.region_labels  # name = Str()
            self.sample_period = (
                self._time_series.sample_period
            )  # sample_period = Float()  采样周期，若规律采样或进行重采样，则间隔一致

            # 选取246个脑区的时间序列要展示的部分

            max_axisY = max(np.ptp(self.timeseries_data, axis=0))  # 最大距离
            y_offset = 0
            timeseries_data_len = len(self.timeseries_data[:, 1])
            self.clearGraphs()
            for i in self.list_br:
                self.addGraph()
                if timeseries_data_len > 10000:
                    step_timeseries = timeseries_data_len // 10000
                    self.graph().setData(
                        self.time_ticks[::step_timeseries],
                        np.add(
                            self.timeseries_data[
                                ::step_timeseries,
                                i,
                            ],
                            y_offset * max_axisY,
                        ),
                    )
                else:
                    self.graph().setData(
                        self.time_ticks,
                        np.add(self.timeseries_data[:, i], y_offset * max_axisY),
                    )
                # self.graph().setBrush(QBrush(QColor(0, 0, 25, 20)))  # 图像阴影的颜色
                y_offset += 1

                self.graph().setLineStyle(QCPGraph.LineStyle(1))  # 线条样式

                # self.setBackground(QColor(0, 0, 0)) # 设置背景颜色
                graphPen = QPen()
                graphPen.setColor(
                    QColor(
                        random.randint(10, 255),
                        random.randint(10, 255),
                        random.randint(10, 255),
                    )
                )  # 线条的颜色 随机
                graphPen.setWidthF(1)
                self.graph().setPen(graphPen)

            self.rescaleAxes()
            self.replot()
