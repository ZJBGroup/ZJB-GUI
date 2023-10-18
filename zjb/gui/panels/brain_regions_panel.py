from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from .brain_regions_panel_ui import Ui_Brain_Regions_Panel


class BrainRegionsPanel(QWidget):
    region_signal_list = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Brain_Regions_Panel()
        self.ui.setupUi(self)
        self.ui.brain_regions_widget.setHeaderHidden(True)
        self.ui.select_all_PrimaryPushButton.clicked.connect(self.get_select_all)
        self.ui.clear_all_PrimaryPushButton.clicked.connect(self.get_clear_all)
        self.ui.brain_regions_widget.itemClicked.connect(self._select_tree_region)

    def show_tree_brain_regions(self, atlas):

        if atlas.subregions:
            self.ui.brain_regions_widget.show_braindata(atlas.subregions)
            self.ui.TitleLabel.setText(atlas.name)
            self.get_select_all()
        else:
            i = 1
            _dict = {}
            dict_labels = {}
            for label in atlas.labels:
                dict_labels[label]=i
                i += 1

            _dict['Regions'] = dict_labels


            self.ui.brain_regions_widget.show_braindata(_dict)
            self.ui.TitleLabel.setText(atlas.name)
            self.get_select_all()

    def _select_tree_region(self):
        [
            text_list_regions,
            number_list_regions,
        ] = self.ui.brain_regions_widget.get_region()
        self.region_signal_list.emit(number_list_regions)

    def get_select_all(self):
        self.ui.brain_regions_widget.get_select_all()
        self._select_tree_region()

    def get_clear_all(self):
        self.ui.brain_regions_widget.get_clear_all()
        self._select_tree_region()
