# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'time_series_page.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_time_series_page(object):
    def setupUi(self, time_series_page):
        time_series_page.setObjectName("time_series_page")
        time_series_page.resize(747, 513)
        self.verticalLayout = QtWidgets.QVBoxLayout(time_series_page)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.StrongBodyLabel = StrongBodyLabel(time_series_page)
        self.StrongBodyLabel.setObjectName("StrongBodyLabel")
        self.horizontalLayout_2.addWidget(self.StrongBodyLabel)
        self.BodyLabel = BodyLabel(time_series_page)
        self.BodyLabel.setObjectName("BodyLabel")
        self.horizontalLayout_2.addWidget(self.BodyLabel)
        self.speed_slider = Slider(time_series_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.speed_slider.sizePolicy().hasHeightForWidth())
        self.speed_slider.setSizePolicy(sizePolicy)
        self.speed_slider.setMinimumSize(QtCore.QSize(201, 24))
        self.speed_slider.setOrientation(QtCore.Qt.Horizontal)
        self.speed_slider.setObjectName("speed_slider")
        self.horizontalLayout_2.addWidget(self.speed_slider)
        self.BodyLabel_2 = BodyLabel(time_series_page)
        self.BodyLabel_2.setObjectName("BodyLabel_2")
        self.horizontalLayout_2.addWidget(self.BodyLabel_2)
        self.StrongBodyLabel_2 = StrongBodyLabel(time_series_page)
        self.StrongBodyLabel_2.setObjectName("StrongBodyLabel_2")
        self.horizontalLayout_2.addWidget(self.StrongBodyLabel_2)
        self.low_color_edit = LineEdit(time_series_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.low_color_edit.sizePolicy().hasHeightForWidth())
        self.low_color_edit.setSizePolicy(sizePolicy)
        self.low_color_edit.setObjectName("low_color_edit")
        self.horizontalLayout_2.addWidget(self.low_color_edit)
        self.StrongBodyLabel_3 = StrongBodyLabel(time_series_page)
        self.StrongBodyLabel_3.setObjectName("StrongBodyLabel_3")
        self.horizontalLayout_2.addWidget(self.StrongBodyLabel_3)
        self.up_color_edit = LineEdit(time_series_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.up_color_edit.sizePolicy().hasHeightForWidth())
        self.up_color_edit.setSizePolicy(sizePolicy)
        self.up_color_edit.setObjectName("up_color_edit")
        self.horizontalLayout_2.addWidget(self.up_color_edit)
        self.update_btn = PrimaryPushButton(time_series_page)
        self.update_btn.setObjectName("update_btn")
        self.horizontalLayout_2.addWidget(self.update_btn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.brain_regions_panel = BrainRegionsPanel(time_series_page)
        self.brain_regions_panel.setObjectName("brain_regions_panel")
        self.horizontalLayout_3.addWidget(self.brain_regions_panel)
        self.atlas_surface_view_widget = AtlasSurfaceViewWidget()
        self.atlas_surface_view_widget.setObjectName("atlas_surface_view_widget")
        self.horizontalLayout_3.addWidget(self.atlas_surface_view_widget)
        self.time_series_widget = TimeSeriesWidget(time_series_page)
        self.time_series_widget.setObjectName("time_series_widget")
        self.horizontalLayout_3.addWidget(self.time_series_widget)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 3)
        self.horizontalLayout_3.setStretch(2, 3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.start_btn = TransparentTogglePushButton(time_series_page)
        self.start_btn.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start_btn.setObjectName("start_btn")
        self.horizontalLayout.addWidget(self.start_btn)
        self.time_slider = Slider(time_series_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.time_slider.sizePolicy().hasHeightForWidth())
        self.time_slider.setSizePolicy(sizePolicy)
        self.time_slider.setMinimumSize(QtCore.QSize(200, 24))
        self.time_slider.setMaximumSize(QtCore.QSize(16777214, 24))
        self.time_slider.setOrientation(QtCore.Qt.Horizontal)
        self.time_slider.setObjectName("time_slider")
        self.horizontalLayout.addWidget(self.time_slider)
        self.time_edit = LineEdit(time_series_page)
        self.time_edit.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.time_edit.sizePolicy().hasHeightForWidth())
        self.time_edit.setSizePolicy(sizePolicy)
        self.time_edit.setMaximumSize(QtCore.QSize(100, 33))
        self.time_edit.setObjectName("time_edit")
        self.horizontalLayout.addWidget(self.time_edit)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(time_series_page)
        QtCore.QMetaObject.connectSlotsByName(time_series_page)

    def retranslateUi(self, time_series_page):
        _translate = QtCore.QCoreApplication.translate
        time_series_page.setWindowTitle(_translate("time_series_page", "Form"))
        self.StrongBodyLabel.setText(_translate("time_series_page", "speed:"))
        self.BodyLabel.setText(_translate("time_series_page", "0"))
        self.BodyLabel_2.setText(_translate("time_series_page", "10"))
        self.StrongBodyLabel_2.setText(_translate("time_series_page", "color range:"))
        self.low_color_edit.setText(_translate("time_series_page", "0"))
        self.StrongBodyLabel_3.setText(_translate("time_series_page", "~"))
        self.up_color_edit.setText(_translate("time_series_page", "5"))
        self.update_btn.setText(_translate("time_series_page", "update"))
        self.start_btn.setText(_translate("time_series_page", "start"))
from qfluentwidgets import BodyLabel, LineEdit, PrimaryPushButton, Slider, StrongBodyLabel, TransparentTogglePushButton
from zjb.gui.panels.brain_regions_panel import BrainRegionsPanel
from zjb.gui.widgets.time_series_widget import TimeSeriesWidget
from zjb.main.visualization.surface_space import AtlasSurfaceViewWidget
