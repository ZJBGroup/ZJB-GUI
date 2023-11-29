from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget
from qfluentwidgets import (
    CustomColorSettingCard,
    ExpandLayout,
    FluentIcon,
    HyperlinkCard,
    OptionsSettingCard,
    PrimaryPushSettingCard,
    ScrollArea,
    SettingCardGroup,
    SwitchSettingCard,
    setTheme,
    setThemeColor,
)

from .._global import GLOBAL_SIGNAL
from ..common.config import cfg, isWin11
from ..common.zjb_style_sheet import myZJBStyleSheet


class AboutUsInterface(ScrollArea):
    """关于我们页面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("About Us")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.settingLabel = QLabel("About Us", self)
        self.settingLabel.move(60, 63)
        self.personalGroup = SettingCardGroup("", self.scrollWidget)

        self.helpCard = HyperlinkCard(
            "https://zjb-docs.readthedocs.io/zh-cn/latest/",
            self.tr("Open ZJB documentation"),
            FluentIcon.HELP,
            self.tr("ZJB documentation"),
            self.tr("Read ZJB documentation to learn how to use ZJB"),
            self.personalGroup,
        )

        self.aboutCard = HyperlinkCard(
            "https://www.zhejianglab.com/home",
            self.tr("About Us"),
            FluentIcon.HOME,
            self.tr("ZHEJIANG LAB"),
            self.tr("Copyright © 2023 by Zhejiang Lab. All Rights Reserved"),
            self.personalGroup,
        )

        self.__initWidget()

    def __initWidget(self):
        """初始化各个控件"""
        self.setWidget(self.scrollWidget)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidgetResizable(True)
        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()
        # self.micaCard.setEnabled(isWin11())

    def __initLayout(self):
        """初始化页面布局"""
        self.personalGroup.addSettingCard(self.helpCard)
        self.personalGroup.addSettingCard(self.aboutCard)
        self.expandLayout.addWidget(self.personalGroup)

    def __setQss(self):
        """设置自定义样式"""
        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")
        myZJBStyleSheet.SETTING_STYLE.apply(self)

    def __connectSignalToSlot(self):
        """绑定槽函数"""
        cfg.themeChanged.connect(self.__onThemeChanged)
        # self.themeColorCard.colorChanged.connect(setThemeColor)
        # self.micaCard.checkedChanged.connect(GLOBAL_SIGNAL.micaEnableChanged)

    def __onThemeChanged(self, theme):
        """主题修改槽函数"""
        setTheme(theme)
