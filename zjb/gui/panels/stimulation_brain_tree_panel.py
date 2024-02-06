from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTreeWidgetItem, QWidget
from qfluentwidgets import CardWidget, TreeWidget


class StimulationBrainRegionsWidget(TreeWidget):
    """刺激页面的树形图"""

    clickedRegionSignal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["StimulationBrainAtlas"])
        self.setColumnCount(1)
        self.setGeometry(0, 0, 300, 700)
        self.setMinimumWidth(200)

    def show_braindata(self, Braindata):
        self.clear()  # 清空树
        self.rootList = []
        root = self
        self.generateTreeWidget(Braindata, root)
        self.insertTopLevelItems(0, self.rootList)
        # 单个点击事件
        self.itemClicked.connect(self.get_clicked_region_info)

    def generateTreeWidget(self, data, root):
        # 判断data是否为字典
        if isinstance(data, dict):
            for key in data.keys():
                child = QTreeWidgetItem()
                child.setText(0, key)
                if isinstance(root, TreeWidget) == False:  # 非根节点，添加子节点
                    root.addChild(child)
                self.rootList.append(child)
                value = data[key]
                self.generateTreeWidget(value, child)

        else:
            root.setText(1, str(data))

    def get_clicked_region_info(self, item: QTreeWidgetItem):
        clicked_region_info = []
        if not item.childCount():
            clicked_region_info = [
                item.parent().parent().text(0),  # anat-profile
                item.parent().text(0),  # subregion
                item.text(0),  # region
                item.text(1),  # brain num
            ]
            self.clickedRegionSignal.emit(clicked_region_info)

    def set_region(self, clickeditem):
        self.collapseAll()
        items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)
        for item_tra in items:
            if item_tra.text(1) == str(clickeditem):
                self.scrollToItem(item_tra)
                self.setCurrentItem(item_tra)
                self.get_clicked_region_info(item_tra)
                if item_tra.parent():
                    text_0 = item_tra.parent().text(0)
                else:
                    text_0 = "no subregion exist"
                if item_tra.parent().parent():
                    text_1 = item_tra.parent().parent().text(0)
                else:
                    text_1 = "No anatomical partitions exist"
                return (
                    item_tra.text(0),
                    text_0,
                    text_1,
                )


class StimulationBrainTreePanel(QWidget):
    """树形图模块"""

    region_signal_list = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUi()
        self.brain_regions_widget.setHeaderHidden(True)

    def _setupUi(self):
        self.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.CardWidget = CardWidget(self)
        self.CardWidget.setObjectName("CardWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.CardWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.brain_regions_widget = StimulationBrainRegionsWidget(self.CardWidget)
        self.brain_regions_widget.setObjectName("brain_regions_widget")
        self.verticalLayout.addWidget(self.brain_regions_widget)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.gridLayout.addWidget(self.CardWidget, 0, 0, 1, 1)

    def show_tree_brain_regions(self, atlas):
        if atlas.subregions:
            self.brain_regions_widget.show_braindata(atlas.subregions)
        else:
            i = 1
            _dict = {}
            dict_labels = {}
            for label in atlas.labels:
                dict_labels[label] = i
                i += 1
            _dict["Regions"] = dict_labels
            self.brain_regions_widget.show_braindata(_dict)
