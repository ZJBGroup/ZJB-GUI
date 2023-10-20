# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'phase_plane_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_phase_plane_widget(object):
    def setupUi(self, phase_plane_widget):
        phase_plane_widget.setObjectName("phase_plane_widget")
        phase_plane_widget.resize(678, 851)
        self.main_layout = QtWidgets.QVBoxLayout(phase_plane_widget)
        self.main_layout.setObjectName("main_layout")
        self.StrongBodyLabel = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel.setObjectName("StrongBodyLabel")
        self.main_layout.addWidget(self.StrongBodyLabel)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.target_variable_x_cbb = ComboBox(phase_plane_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.target_variable_x_cbb.sizePolicy().hasHeightForWidth())
        self.target_variable_x_cbb.setSizePolicy(sizePolicy)
        self.target_variable_x_cbb.setObjectName("target_variable_x_cbb")
        self.horizontalLayout_2.addWidget(self.target_variable_x_cbb)
        self.StrongBodyLabel_2 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_2.setObjectName("StrongBodyLabel_2")
        self.horizontalLayout_2.addWidget(self.StrongBodyLabel_2)
        self.tvx_start_edit = LineEdit(phase_plane_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tvx_start_edit.sizePolicy().hasHeightForWidth())
        self.tvx_start_edit.setSizePolicy(sizePolicy)
        self.tvx_start_edit.setObjectName("tvx_start_edit")
        self.horizontalLayout_2.addWidget(self.tvx_start_edit)
        self.StrongBodyLabel_3 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_3.setObjectName("StrongBodyLabel_3")
        self.horizontalLayout_2.addWidget(self.StrongBodyLabel_3)
        self.tvx_end_edit = LineEdit(phase_plane_widget)
        self.tvx_end_edit.setObjectName("tvx_end_edit")
        self.horizontalLayout_2.addWidget(self.tvx_end_edit)
        self.StrongBodyLabel_6 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_6.setObjectName("StrongBodyLabel_6")
        self.horizontalLayout_2.addWidget(self.StrongBodyLabel_6)
        self.tvx_step_edit = LineEdit(phase_plane_widget)
        self.tvx_step_edit.setObjectName("tvx_step_edit")
        self.horizontalLayout_2.addWidget(self.tvx_step_edit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.main_layout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.target_variable_y_cbb = ComboBox(phase_plane_widget)
        self.target_variable_y_cbb.setObjectName("target_variable_y_cbb")
        self.horizontalLayout_3.addWidget(self.target_variable_y_cbb)
        self.StrongBodyLabel_4 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_4.setObjectName("StrongBodyLabel_4")
        self.horizontalLayout_3.addWidget(self.StrongBodyLabel_4)
        self.tvy_start_edit = LineEdit(phase_plane_widget)
        self.tvy_start_edit.setObjectName("tvy_start_edit")
        self.horizontalLayout_3.addWidget(self.tvy_start_edit)
        self.StrongBodyLabel_5 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_5.setObjectName("StrongBodyLabel_5")
        self.horizontalLayout_3.addWidget(self.StrongBodyLabel_5)
        self.tvy_end_edit = LineEdit(phase_plane_widget)
        self.tvy_end_edit.setObjectName("tvy_end_edit")
        self.horizontalLayout_3.addWidget(self.tvy_end_edit)
        self.StrongBodyLabel_7 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_7.setObjectName("StrongBodyLabel_7")
        self.horizontalLayout_3.addWidget(self.StrongBodyLabel_7)
        self.tvy_step_edit = LineEdit(phase_plane_widget)
        self.tvy_step_edit.setObjectName("tvy_step_edit")
        self.horizontalLayout_3.addWidget(self.tvy_step_edit)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.main_layout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.StrongBodyLabel_9 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_9.setObjectName("StrongBodyLabel_9")
        self.horizontalLayout_5.addWidget(self.StrongBodyLabel_9)
        self.trajectory_points_x_edit = LineEdit(phase_plane_widget)
        self.trajectory_points_x_edit.setObjectName("trajectory_points_x_edit")
        self.horizontalLayout_5.addWidget(self.trajectory_points_x_edit)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem2)
        self.main_layout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.StrongBodyLabel_11 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_11.setObjectName("StrongBodyLabel_11")
        self.horizontalLayout_6.addWidget(self.StrongBodyLabel_11)
        self.trajectory_points_y_edit = LineEdit(phase_plane_widget)
        self.trajectory_points_y_edit.setObjectName("trajectory_points_y_edit")
        self.horizontalLayout_6.addWidget(self.trajectory_points_y_edit)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem3)
        self.main_layout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.StrongBodyLabel_10 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_10.setObjectName("StrongBodyLabel_10")
        self.horizontalLayout_7.addWidget(self.StrongBodyLabel_10)
        self.trajectory_duration_edit = LineEdit(phase_plane_widget)
        self.trajectory_duration_edit.setObjectName("trajectory_duration_edit")
        self.horizontalLayout_7.addWidget(self.trajectory_duration_edit)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem4)
        self.main_layout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.start_btn = PrimaryPushButton(phase_plane_widget)
        self.start_btn.setObjectName("start_btn")
        self.horizontalLayout.addWidget(self.start_btn)
        spacerItem5 = QtWidgets.QSpacerItem(220, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.main_layout.addLayout(self.horizontalLayout)
        self.pp_mplWidget = MplWidget(phase_plane_widget)
        self.pp_mplWidget.setMinimumSize(QtCore.QSize(100, 100))
        self.pp_mplWidget.setObjectName("pp_mplWidget")
        self.main_layout.addWidget(self.pp_mplWidget)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.StrongBodyLabel_8 = StrongBodyLabel(phase_plane_widget)
        self.StrongBodyLabel_8.setObjectName("StrongBodyLabel_8")
        self.horizontalLayout_4.addWidget(self.StrongBodyLabel_8)
        self.fixed_points_edit = LineEdit(phase_plane_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fixed_points_edit.sizePolicy().hasHeightForWidth())
        self.fixed_points_edit.setSizePolicy(sizePolicy)
        self.fixed_points_edit.setText("")
        self.fixed_points_edit.setReadOnly(True)
        self.fixed_points_edit.setObjectName("fixed_points_edit")
        self.horizontalLayout_4.addWidget(self.fixed_points_edit)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem6)
        self.main_layout.addLayout(self.horizontalLayout_4)
        spacerItem7 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addItem(spacerItem7)

        self.retranslateUi(phase_plane_widget)
        QtCore.QMetaObject.connectSlotsByName(phase_plane_widget)

    def retranslateUi(self, phase_plane_widget):
        _translate = QtCore.QCoreApplication.translate
        phase_plane_widget.setWindowTitle(_translate("phase_plane_widget", "Form"))
        self.StrongBodyLabel.setText(_translate("phase_plane_widget", "Stata variables shown on axes and their range"))
        self.target_variable_x_cbb.setText(_translate("phase_plane_widget", "Target Variable x"))
        self.StrongBodyLabel_2.setText(_translate("phase_plane_widget", "start:"))
        self.StrongBodyLabel_3.setText(_translate("phase_plane_widget", "end:"))
        self.StrongBodyLabel_6.setText(_translate("phase_plane_widget", "step:"))
        self.target_variable_y_cbb.setText(_translate("phase_plane_widget", "Target Variable y"))
        self.StrongBodyLabel_4.setText(_translate("phase_plane_widget", "start:"))
        self.StrongBodyLabel_5.setText(_translate("phase_plane_widget", "end:"))
        self.StrongBodyLabel_7.setText(_translate("phase_plane_widget", "step:"))
        self.StrongBodyLabel_9.setText(_translate("phase_plane_widget", "Trajectory Initial Points x"))
        self.StrongBodyLabel_11.setText(_translate("phase_plane_widget", "Trajectory Initial Points y"))
        self.StrongBodyLabel_10.setText(_translate("phase_plane_widget", "Trajectory Duration"))
        self.start_btn.setText(_translate("phase_plane_widget", "Start Phase Plane Analysis"))
        self.StrongBodyLabel_8.setText(_translate("phase_plane_widget", "Fixed Points"))
from qfluentwidgets import ComboBox, LineEdit, PrimaryPushButton, StrongBodyLabel
from zjb.gui.widgets.mpl_widget import MplWidget
