# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'brain_regions_panel.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Brain_Regions_Panel(object):
    def setupUi(self, Brain_Regions_Panel):
        Brain_Regions_Panel.setObjectName("Brain_Regions_Panel")
        Brain_Regions_Panel.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(Brain_Regions_Panel)
        self.gridLayout.setObjectName("gridLayout")
        self.CardWidget = CardWidget(Brain_Regions_Panel)
        self.CardWidget.setObjectName("CardWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.CardWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.TitleLabel = TitleLabel(self.CardWidget)
        self.TitleLabel.setObjectName("TitleLabel")
        self.verticalLayout.addWidget(self.TitleLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.select_all_PrimaryPushButton = PrimaryPushButton(self.CardWidget)
        self.select_all_PrimaryPushButton.setObjectName("select_all_PrimaryPushButton")
        self.horizontalLayout.addWidget(self.select_all_PrimaryPushButton)
        self.clear_all_PrimaryPushButton = PrimaryPushButton(self.CardWidget)
        self.clear_all_PrimaryPushButton.setObjectName("clear_all_PrimaryPushButton")
        self.horizontalLayout.addWidget(self.clear_all_PrimaryPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.brain_regions_widget = BrainRegionsWidget(self.CardWidget)
        self.brain_regions_widget.setObjectName("brain_regions_widget")
        self.verticalLayout.addWidget(self.brain_regions_widget)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.gridLayout.addWidget(self.CardWidget, 0, 0, 1, 1)

        self.retranslateUi(Brain_Regions_Panel)
        QtCore.QMetaObject.connectSlotsByName(Brain_Regions_Panel)

    def retranslateUi(self, Brain_Regions_Panel):
        _translate = QtCore.QCoreApplication.translate
        Brain_Regions_Panel.setWindowTitle(_translate("Brain_Regions_Panel", "Form"))
        self.TitleLabel.setText(_translate("Brain_Regions_Panel", "Brain Regions"))
        self.select_all_PrimaryPushButton.setText(_translate("Brain_Regions_Panel", " Select All"))
        self.clear_all_PrimaryPushButton.setText(_translate("Brain_Regions_Panel", "Clear All"))
from qfluentwidgets import CardWidget, PrimaryPushButton, TitleLabel
from zjb.gui.widgets.brain_regions_widget import BrainRegionsWidget
