# coding:utf-8
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    IconWidget,
    ScrollArea,
    SubtitleLabel,
    TabBar,
    TabCloseButtonDisplayMode,
    setFont,
)

from .._rc import find_resource_file


class TabInterface(QFrame):
    """Tab interface"""

    def __init__(self, text: str, icon, objectName, parent=None):
        super().__init__(parent=parent)
        self.iconWidget = IconWidget(icon, self)
        self.label = SubtitleLabel(text, self)
        self.iconWidget.setFixedSize(120, 120)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignCenter)
        setFont(self.label, 24)

        self.setObjectName(objectName)


class WinInterface(ScrollArea):
    """窗口区域"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("WinInterface")
        self.setStyleSheet("#WinInterface{background:transparent;border:none}")
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.win_panel = QWidget(self)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.win_panel.sizePolicy().hasHeightForWidth())
        self.win_panel.setSizePolicy(sizePolicy)
        self.win_panel.setObjectName("win_panel")
        self.win_panel_layout = QVBoxLayout(self.win_panel)
        self.win_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.win_panel_layout.setObjectName("win_panel_layout")

        # add tab bar
        self.tabBar = TabBar(self)
        self.tabBar.setMovable(True)
        self.tabBar.setTabMaximumWidth(220)
        self.tabBar.setTabShadowEnabled(False)
        self.tabBar.setTabSelectedBackgroundColor(
            QColor(255, 255, 255, 125), QColor(255, 255, 255, 50)
        )
        # self.tabBar.setScrollable(True)
        # self.tabBar.setAddButtonVisible(False)
        self.tabBar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)
        self.tabBar.tabCloseRequested.connect(self.tabBar.removeTab)
        self.tabBar.currentChanged.connect(lambda i: print(self.tabBar.tabText(i)))

        self.homeInterface = QStackedWidget(self, objectName="homeInterface")

        self.win_panel_layout.addWidget(self.tabBar)
        self.win_panel_layout.addWidget(self.homeInterface)

        self.horizontalLayout.addWidget(self.win_panel)

        self.addTab("Welcome", "Welcome", QIcon(find_resource_file("icon/logo.jpg")))
        self.tabBar.currentChanged.connect(self.onTabChanged)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False
        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)

    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()
        self.homeInterface.setCurrentWidget(self.findChild(TabInterface, objectName))

    def onTabAddRequested(self):
        text = f"panel×{self.tabBar.count()}"
        self.addTab(text, text, QIcon(":/zjb/gui/icon/logo.jpg"))

    def addTab(self, routeKey, text, icon):
        self.tabBar.addTab(routeKey, text, icon)
        self.homeInterface.addWidget(TabInterface(text, icon, routeKey, self))
