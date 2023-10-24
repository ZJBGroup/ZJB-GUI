# coding:utf-8
import sys

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    FluentIcon,
    FluentWindow,
    MSFluentTitleBar,
    NavigationItemPosition,
    ScrollArea,
    TabBar,
    TabCloseButtonDisplayMode,
)
from zjb.gui._global import GLOBAL_SIGNAL
from zjb.gui._rc import find_resource_file
from zjb.gui.pages.base_page import BasePage
from zjb.gui.pages.setting_page import SettingInterface
from zjb.gui.pages.welcome_page import WelcomePage
from zjb.gui.panels.atlas_list_panel import AtlasInterface
from zjb.gui.panels.dtb_list_panel import DTBInterface
from zjb.gui.panels.dynamic_model_list_panel import DynamicModelInterface
from zjb.gui.panels.job_manager_list_panel import JobManagerInterface
from zjb.gui.widgets.titlebar_button import NewButton, OpenButton
from zjb.main.manager.workspace import Workspace


class CustomTitleBar(MSFluentTitleBar):
    """标题栏和工具栏"""

    def __init__(self, parent):
        super().__init__(parent)

        self.newButton = NewButton("New")
        self.openButton = OpenButton("Open")

        self.toolButtonLayout = QHBoxLayout()
        self.toolButtonLayout.setContentsMargins(0, 0, 0, 0)
        self.toolButtonLayout.setSpacing(0)
        self.toolButtonLayout.addWidget(self.newButton)
        self.toolButtonLayout.addWidget(self.openButton)
        self.hBoxLayout.insertLayout(4, self.toolButtonLayout)


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

        self.tabBar = TabBar(self)
        self.tabBar.setMovable(True)
        self.tabBar.setTabMaximumWidth(220)
        self.tabBar.setTabShadowEnabled(False)
        self.tabBar.setTabSelectedBackgroundColor(
            QColor(255, 255, 255, 125), QColor(255, 255, 255, 50)
        )
        # self.tabBar.setScrollable(True)
        self.tabBar.setAddButtonVisible(False)
        self.tabBar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)
        self.tabBar.tabCloseRequested.connect(self._closePage)
        self.tabBar.currentChanged.connect(self._onTabChanged)

        self.stackedWindows = QStackedWidget(self, objectName="stackedWindows")
        self.win_panel_layout.addWidget(self.tabBar)
        self.win_panel_layout.addWidget(self.stackedWindows)
        self.horizontalLayout.addWidget(self.win_panel)
        self.addPage("Welcome", self._addWelcomePage)

    def _addWelcomePage(self, routeKey: str):
        """新建欢迎页面的回调函数"""
        welcome_page = WelcomePage(routeKey, "Welcome", FluentIcon.HOME)
        return welcome_page

    def canDrag(self, pos: QPoint):
        """tab拖拽方法"""
        if not super().canDrag(pos):
            return False
        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)

    def _onTabChanged(self, index: int):
        """tab切换操作"""
        objectName = self.tabBar.currentTab().routeKey()
        _page: BasePage = self.findChild(BasePage, name=objectName)
        self.stackedWindows.setCurrentWidget(_page)
        _page.currentPageSignal.emit()

    def _closePage(self, index):
        """
        点击Tab的关闭按钮，关闭对应的页面
        :param: index: 所点击Tab的索引
        """
        page_routeKey = self.tabBar.tabItem(index).routeKey()
        close_page = self.findChild(BasePage, name=page_routeKey)
        self.stackedWindows.removeWidget(close_page)
        close_page.deleteLater()
        self.tabBar.removeTab(index)

    def _openPage(self, page: BasePage):
        """
        打开指定页面，点亮指定 Tab
        :param: page: Tab对应的页面
        """
        self.stackedWindows.setCurrentWidget(page)
        page.currentPageSignal.emit()
        self.tabBar.setCurrentTab(page.getRouteKey())

    def addPage(self, routeKey: str, callback):
        """在层叠窗口区增加一个窗口

        Parameters:
        ----------
        routeKey: str
            增加窗口的唯一标识 routeKey
        callback: function
            用于创建窗口的回调函数
        """
        flag = self.findChild(BasePage, name=routeKey)
        # 若该页面已打开则直接跳转到该页面
        if flag == None:
            page: BasePage = callback(routeKey)
            self.stackedWindows.addWidget(page)
            self.tabBar.addTab(page.getRouteKey(), page.getTitle(), page.getIcon())
            flag = page
        self._openPage(flag)


class MainWindow(FluentWindow):
    """主窗口"""

    def __init__(self, parent=None):
        self.isMicaEnabled = False
        super().__init__()
        self.initWindow()

        self.dtbWinInterface = DTBInterface(self)
        self.atlasInterface = AtlasInterface(self)
        self.dynamicModelInterface = DynamicModelInterface(self)
        self.jobManagerInterface = JobManagerInterface(self)
        self.settingPage = SettingInterface(self)

        # 禁用 win11 的 Mica 特效
        # self.setMicaEffectEnabled(False)

        self.initNavigation()

        GLOBAL_SIGNAL.workspaceChanged[Workspace].connect(self.setWorkspace)
        GLOBAL_SIGNAL.requestAddPage.connect(self.addPage)

    def initWindow(self):
        """初始化窗口"""

        self.setTitleBar(CustomTitleBar(self))
        self.resize(1150, 750)
        self.setWindowIcon(QIcon(find_resource_file("icon/logo.jpg")))
        self.setWindowTitle("Zhejiang Lab Brain")

        # 重新布局保证目录栏宽度可伸缩
        self.widgetLayout = QSplitter(self)
        self.widgetLayout.setOrientation(Qt.Horizontal)
        self.widgetLayout.setObjectName("widgetLayout")
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)
        self.stackedWidget.setMinimumWidth(250)
        self.widgetLayout.addWidget(self.stackedWidget)
        self.widgetLayout.setStyleSheet("background-color: transparent")
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)

        # 右侧的窗口群
        self.widgetWindows = WinInterface(self)
        self.widgetLayout.addWidget(self.widgetWindows)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def addPage(self, routeKey: str, callback):
        """调用子组件的方法，在层叠窗口区增加一个窗口

        Parameters:
        ----------
        routeKey: str
            增加窗口的唯一标识 routeKey
        callback: function
            用于创建窗口的回调函数
        """
        self.widgetWindows.addPage(routeKey, callback)

    def initNavigation(self):
        """初始化左侧导航栏"""

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(
            self.dtbWinInterface, FluentIcon.GLOBE, "Digital Twin Brain", pos
        )
        self.addSubInterface(self.atlasInterface, FluentIcon.IOT, "Atlas", pos)
        self.addSubInterface(
            self.dynamicModelInterface, FluentIcon.CALORIES, "Dynamic Model", pos
        )
        self.addSubInterface(
            self.jobManagerInterface, FluentIcon.SEND, "Job Manager", pos
        )
        self.addSubInterface(
            self.settingPage,
            FluentIcon.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM,
        )
        self.stackedWidget.currentChanged.connect(self.navChanged)
        self.navigationInterface.setReturnButtonVisible(False)  # 取消返回按钮

    def navChanged(self, navNum):
        """
        监测点击左侧导航时，返回点击的索引数，点击设置页面的时候需要隐藏 tab 窗口区
        :param: navNum: 所点击导航的索引数
        """
        if navNum == self.stackedWidget.count() - 1:
            self.widgetWindows.hide()
        else:
            self.widgetWindows.show()

    def setWorkspace(self, workspace: Workspace):
        self._work_space = workspace
        print("self._work_space==============", self._work_space.name)
        self.dynamicModelInterface.setWorkspace(workspace)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()
