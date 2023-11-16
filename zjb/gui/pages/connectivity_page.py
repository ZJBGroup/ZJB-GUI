import collections

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from qfluentwidgets import FluentIcon

from zjb.main.api import Connectivity

from ..libs import pycircos
from .base_page import BasePage
from .connectivity_page_ui import Ui_connectivity_page


class ConnectivityPage(BasePage):
    def __init__(self, connectivity: Connectivity):
        super().__init__(connectivity._gid.str, "Connectivity", FluentIcon.FIT_PAGE)
        self.connectivity = connectivity
        self.atlas = connectivity.space.atlas

        self._connectivity = None
        self.br_selected = None

        self._setup_ui()
        self.setObjectName(connectivity._gid.str)

    def _setup_ui(self):
        self.ui = Ui_connectivity_page()
        self.ui.setupUi(self)
        self.ui.splitter.setSizes([500, 2000, 2000])

        self.ui.brain_regions_panel.region_signal_list.connect(
            self._on_region_signal_change
        )
        self.ui.brain_regions_panel.show_tree_brain_regions(self.atlas)

        self._set_connectivity()

    def _set_connectivity(self):
        """设置要可视化的连接矩阵"""
        self.ui.connectivity_widget.setConnectivity(self.connectivity)
        if isinstance(self.br_selected, list):
            self._get_connectivity_data()

    def select_regions(self, selected_regions):
        self.ui.connectivity_widget.setSelectRegion(selected_regions)
        self.br_selected = selected_regions

        if self.connectivity is not None:
            self._get_connectivity_data()

    def _get_connectivity_data(self):
        # 根据br_selected获得要显示的数据
        self.br_name_selected = np.squeeze(self.atlas.labels[[self.br_selected]])
        self._circos_update()

    def _circos_update(self):
        for i in reversed(range(self.ui.circos_widget.vertical_layout.count())):
            self.ui.circos_widget.vertical_layout.removeWidget(
                self.ui.circos_widget.vertical_layout.itemAt(i).widget().deleteLater()
            )

        Garc = pycircos.Garc
        Gcircle = pycircos.Gcircle

        # Set chromosomes
        circle = Gcircle(figsize=(8, 8))
        for region_label in self.atlas.labels:
            arc = Garc(
                arc_id=region_label,
                size=20,
                interspace=0.5,
                raxis_range=(735, 785),
                labelposition=100,
                label_visible=True,
                labelsize=5,
            )
            circle.add_garc(arc)
        circle.set_garcs(0, 360)

        # linkplot
        values_all = []
        br_selected = np.sort(self.br_selected)
        arcdata_dict = collections.defaultdict(dict)

        f = self.connectivity.data
        f_1 = np.triu(f, 1)
        link_selected = np.squeeze(f_1[[br_selected]])

        for br_num in range(30):
            if len(br_selected) == 0:
                pass
            else:
                if len(br_selected) == 1:
                    np.max(link_selected)
                    positions = np.where(link_selected == np.max(link_selected))
                    name1_index = int(br_selected)
                    name2_index = int(positions[0])
                    link_selected[name2_index] = 0

                else:
                    np.max(link_selected)
                    positions = np.where(link_selected == np.max(link_selected))
                    positions_1 = int(positions[0])
                    name1_index = br_selected[positions_1]
                    name2_index = int(positions[1])
                    link_selected[positions_1, name2_index] = 0

                name1 = "".join(self.atlas.labels[name1_index].rstrip())
                name2 = "".join(self.atlas.labels[name2_index].rstrip())

                source = (name1, 5, 15, 735)
                destination = (name2, 5, 15, 735)
                circle.chord_plot(
                    source,
                    destination,
                    facecolor=circle.garc_dict[name1].facecolor,
                    edgecolor=circle.garc_dict[name1].facecolor,
                    linewidth=0.5,
                )

        ax = plt.gca()
        ax.set_facecolor("black")
        texts = ax.findobj(match=plt.Text)
        for text in texts:
            text.set_color("white")
        circle.figure.set_facecolor("black")
        canvas = FigureCanvas(circle.figure)

        self.ui.circos_widget.vertical_layout.addWidget(canvas)

    def _on_region_signal_change(self, number_list_regions):
        self.select_regions(number_list_regions)
