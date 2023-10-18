import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTreeWidgetItem
from qfluentwidgets import TreeWidget


class BrainRegionsWidget(TreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setHeaderLabels(["BrainAtlas"])
        self.setColumnCount(1)
        self.setGeometry(0, 0, 300, 700)

    def show_braindata(self, Braindata):
        self.clear()  # 清空树
        self.rootList = []
        root = self
        self.generateTreeWidget(Braindata, root)

        # print(self.rootList)
        self.insertTopLevelItems(0, self.rootList)
        # 单个点击事件
        self.itemClicked.connect(self.get_region)
        # 复选框点击事件
        self.itemChanged.connect(self.get_selected_regions)

    def generateTreeWidget(self, data, root):
        # 判断data是否为字典
        if isinstance(data, dict):
            for key in data.keys():
                child = QTreeWidgetItem()
                child.setText(0, key)
                child.setCheckState(0, Qt.Unchecked)
                if isinstance(root, TreeWidget) == False:  # 非根节点，添加子节点
                    root.addChild(child)
                self.rootList.append(child)
                # print(key)
                value = data[key]
                self.generateTreeWidget(value, child)

        else:
            root.setText(1, str(data))

    def get_region(self):
        # print(item.text(0))
        text_list_regions = []
        number_list_regions = []
        items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)
        for item_tra in items:
            # 获得底层项目中复选框被选中的Item
            # item.childCount()：判断其没有分支
            if (
                item_tra.parent()
                and not item_tra.childCount()
                and item_tra.checkState(0) == 2
            ):
                text_list_regions.append(item_tra.text(0))
                number_list_regions.append(int(item_tra.text(1)) - 1)
        # print(text_list_regions)
        # print(self.Treewidget.currentItem().text(0))
        return text_list_regions, number_list_regions
        # return 单个脑区的字符串

    def get_selected_regions(self, item, column):  # getGroupRegions
        count = item.childCount()
        for f in range(count):
            if item.checkState(column) == Qt.Checked:
                item.child(f).setCheckState(0, Qt.Checked)
            else:
                item.child(f).setCheckState(0, Qt.Unchecked)

    def set_region(self, clickeditem):
        # self.get_clear_all()
        self.collapseAll()
        items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)
        for item_tra in items:
            if item_tra.text(1) == str(clickeditem):
                item_tra.setCheckState(0, Qt.Checked)
                self.scrollToItem(item_tra)
                if item_tra.parent():
                    text_0 = item_tra.parent().text(0)
                else:
                    text_0 = 'no subregion exist'

                if item_tra.parent().parent():
                    text_1 = item_tra.parent().parent().text(0)
                else:
                    text_1 = 'No anatomical partitions exist'

                return (
                    item_tra.text(0),
                    text_0,
                    text_1,
                )

    def set_regions(self, listRegion):
        self.get_clear_all()
        # print(list)
        items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)

        for item in items:
            if item.text(1) != "":
                if int(item.text(1)) - 1 in listRegion:
                    item.setCheckState(0, Qt.Checked)
                    self.scrollToItem(item)

    def get_select_all(self):
        items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)
        for item in items:
            item.setCheckState(0, Qt.Checked)

    def get_clear_all(self):
        items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)
        for item in items:
            item.setCheckState(0, Qt.Unchecked)
