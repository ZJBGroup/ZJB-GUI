import typing

import numpy as np
from pyqtgraph.Qt import QtGui
from zjb.main.api import Connectivity
import pyqtgraph as pg
ConnectivityOrNone = typing.Optional[Connectivity]


class ConnectivityWidget(pg.GraphicsLayoutWidget):

    _connectivity: ConnectivityOrNone

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # self.gr_wid = pg.GraphicsLayoutWidget(parent=self)  # 创造一个2维可视化控件
        # self.gr_wid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addLabel("Connectivity Views", colspan=2)
        self.nextRow()  # 标题
        self._connectivity = None
        self.br_selected = None

    def setConnectivity(self, connectivity: ConnectivityOrNone):
        """设置要可视化的连接矩阵"""
        self._connectivity = connectivity
        if isinstance(self.br_selected, list):
            self._get_connectivity_data()

    def setSelectRegion(self, select_region):
        """被选择的脑区"""
        self.br_selected = select_region
        if self._connectivity is not None:
            self._get_connectivity_data()

    def _get_connectivity_data(self):
        # 根据br_selected获得要显示的数据
        if len(self.br_selected) > 1:
            self.br_names = self._connectivity.space.atlas.labels
            self.weights_all = self._connectivity.data # 全部脑区名字和权重矩阵
            self.br_name_selected = np.squeeze(self.br_names[[self.br_selected]])
            self.corrMatrix_selected = np.squeeze(self.weights_all[[self.br_selected]])
            self.corrMatrix_selected = np.squeeze(self.corrMatrix_selected[:, [self.br_selected]])  # 被选中脑区的数据
            self.clear() # 在画之前清除画布
            self._update()
        else:
            self.clear()

    def _update(self):

        self.columns = self.br_name_selected # 被选中脑区的名字
        self.weights = self.corrMatrix_selected

        pg.setConfigOption('imageAxisOrder', 'row-major')  # Switch default order to Row-major

        self.correlogram = pg.ImageItem()
        self.tr = QtGui.QTransform().translate(-0.5, -0.5)
        self.correlogram.setTransform(self.tr)
        self.correlogram.setImage(self.weights)

        self.plotItem = self.addPlot()  # add PlotItem to the main GraphicsLayoutWidget
        self.plotItem.clearPlots()
        self.plotItem.setDefaultPadding(0.0)  # plot without padding data range
        self.plotItem.addItem(self.correlogram)  # display correlogram

        # show full frame, label tick marks at top and left sides, with some extra space for labels:
        self.plotItem.showAxes(True, showValues=(True, True, False, False), size=20)

        # define major tick marks and labels:
        self.ticks = [(idx, label) for idx, label in enumerate(self.columns)]
        if len(self.ticks) <= 35:
            for side in ('left', 'top', 'right', 'bottom'):
                self.plotItem.getAxis(side).setTicks((self.ticks, []))  # add list of major ticks; no minor ticks
        self.plotItem.getAxis('bottom').setHeight(10)  # include some additional space at bottom of figure

        self.colorMap = pg.colormap.get("viridis")  # choose perceptually uniform, diverging color map

        self.bar = pg.ColorBarItem(values=(self.weights.min(), self.weights.max()), colorMap=self.colorMap)
        # link color bar and color map to correlogram, and show it in plotItem:
        self.bar.setImageItem(self.correlogram, insert_in=self.plotItem)

