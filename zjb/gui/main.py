# coding:utf-8
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QSplitter
from qfluentwidgets import (
    Action,
    FluentIcon,
    FluentWindow,
    MSFluentTitleBar,
    NavigationItemPosition,
    RoundMenu,
    Theme,
    TransparentDropDownPushButton,
    setTheme,
)

from zjb.gui._rc import find_resource_file
from zjb.gui.pages.setting_page import SettingInterface
from zjb.gui.pages.win_page import WinInterface
from zjb.gui.panels.atlas_list_panel import AtlasInterface
from zjb.gui.panels.dtb_list_panel import DTBInterface
from zjb.gui.panels.dynamic_model_list_panel import DynamicModelInterface
from zjb.gui.panels.job_manager_list_panel import JobManagerInterface


class NewButton(TransparentDropDownPushButton):
    """New 按钮及其下拉菜单"""

    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.newMenu = RoundMenu(parent=self)
        self.newMenu.addAction(Action(FluentIcon.FOLDER, "WorkSpace"))
        self.newMenu.addAction(Action(FluentIcon.TILES, "Project"))
        self.newMenu.addAction(Action(FluentIcon.PEOPLE, "Subject"))
        self.newMenu.addAction(Action(FluentIcon.LIBRARY, "DTB Model"))
        self.newMenu.addAction(Action(FluentIcon.LEAF, "DTB"))
        self.setMenu(self.newMenu)


class OpenButton(TransparentDropDownPushButton):
    """Open 按钮及其下拉菜单"""

    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.openMenu = RoundMenu(parent=self)
        self.openMenu.addAction(Action(FluentIcon.FOLDER, "WorkSpace"))
        submenu = RoundMenu("Recent", self)
        submenu.setIcon(FluentIcon.FOLDER)
        # TODO :不用二级菜单去展示最近打开的工作空间
        submenu.addActions(
            [
                Action(FluentIcon.VIDEO, "Video"),
                Action(FluentIcon.MUSIC, "Music"),
            ]
        )
        self.openMenu.addMenu(submenu)
        self.setMenu(self.openMenu)


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


class MainWindow(FluentWindow):
    """主窗口"""

    def __init__(self, parent=None):
        self.isMicaEnabled = False
        super().__init__()
        self.initWindow()

        self.dtbWinInterface = DTBInterface(self)
        self.dtbWinInterface2 = DTBInterface(self)
        self.atlasInterface = AtlasInterface(self)
        self.dynamicModelInterface = DynamicModelInterface(self)
        self.jobManagerInterface = JobManagerInterface(self)
        self.settingPage = SettingInterface(self)

        # 禁用 win11 的 Mica 特效
        # self.setMicaEffectEnabled(False)

        self.initNavigation()

    def initWindow(self):
        """初始化窗口"""

        self.setTitleBar(CustomTitleBar(self))
        self.resize(1100, 750)
        self.setWindowIcon(QIcon(find_resource_file("icon/logo.jpg")))
        self.setWindowTitle("Zhejiang Lab Brain")

        # 重新布局保证目录栏宽度可伸缩
        self.widgetLayout = QSplitter(self)
        self.widgetLayout.setOrientation(Qt.Horizontal)
        self.widgetLayout.setObjectName("widgetLayout")
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)
        self.widgetLayout.addWidget(self.stackedWidget)
        self.widgetLayout.setStyleSheet("background-color: transparent")
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)

        # 右侧的窗口群
        self.widgetWindows = WinInterface(self)
        self.widgetLayout.addWidget(self.widgetWindows)
        self.stackedWidget.setMinimumWidth(250)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def initNavigation(self):
        """初始化左侧导航栏"""

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(
            self.dtbWinInterface, FluentIcon.GLOBE, "Digital Twin Brain", pos
        )
        self.addSubInterface(self.dtbWinInterface2, FluentIcon.GAME, "Faker", pos)
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


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()
