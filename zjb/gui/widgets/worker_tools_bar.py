from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import FluentIcon, InfoBadge, PrimaryPushButton, SpinBox


class WorkerToolsBar(QWidget):
    def __init__(self, max_card_num, parent=None):
        super().__init__(parent)

        # 工具栏布局
        self.toolsBar = QHBoxLayout(self)
        self.toolsBar.setAlignment(Qt.AlignLeft)
        self.toolsBar.setSpacing(10)
        self.toolsBar.setContentsMargins(0, 0, 0, 0)

        # 自定义增减板块
        self.spinBox = SpinBox()
        self.spinBox.setMaximum(int(max_card_num))
        self.spinBox.setDisabled(True)

        # 按钮
        self.primaryToolButton = PrimaryPushButton(
            "Delete Idle", self, FluentIcon.DELETE
        )

        # 允许的最大数目的 badge
        self.max_badge = InfoBadge.attension(f"Max:{max_card_num}")
        self.max_badge.setFont(QFont("", 14, QFont.Weight.Normal))
        # 总数的 badge
        self.all_badge = InfoBadge.custom("All:0", "#005fb8", "#60cdff")
        self.all_badge.setFont(QFont("", 14, QFont.Weight.Normal))
        # 忙碌的 badge
        self.busy_badge = InfoBadge.error("Busy:0")
        self.busy_badge.setFont(QFont("", 14, QFont.Weight.Normal))
        # 空闲的 badge
        self.idle_badge = InfoBadge.success("Idle:0")
        self.idle_badge.setFont(QFont("", 14, QFont.Weight.Normal))

        # 工具栏布局
        self.toolsBar.addWidget(self.spinBox)
        self.toolsBar.addWidget(self.primaryToolButton)
        self.toolsBar.addStretch()
        self.toolsBar.addWidget(self.max_badge)
        self.toolsBar.addWidget(self.all_badge)
        self.toolsBar.addWidget(self.busy_badge)
        self.toolsBar.addWidget(self.idle_badge)

    def setSpinBoxDisabled(self, flag: bool):
        self.spinBox.setDisabled(flag)

    def getSpinBoxNum(self):
        return int(self.spinBox.text())

    def updateToolsBar(self, count=None, all_num=None, busy_num=None, idle_num=None):
        """
        更新工具栏中的各项数据
        :param: count: spinBox中的可编辑的数据
        :param: all_num: badge中的总数
        :param: busy_num: badge中运行中的进程数
        :param: idel_num: badge中的空闲进程数
        """
        if not count == None:
            self.spinBox.setValue(count)
        if not all_num == None:
            self.all_badge.setText(f"All:{all_num}")
        if not busy_num == None:
            self.busy_badge.setText(f"Busy:{busy_num}")
        if not idle_num == None:
            self.idle_badge.setText(f"Idle:{idle_num}")
