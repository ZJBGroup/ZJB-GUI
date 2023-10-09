from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget
from qfluentwidgets import (
    CustomColorSettingCard,
    ExpandLayout,
    FluentIcon,
    OptionsSettingCard,
    ScrollArea,
    SettingCardGroup,
    setTheme,
    setThemeColor,
)

from ..common.config import cfg
from ..common.zjb_style_sheet import myZJBStyleSheet


class SettingInterface(ScrollArea):
    """设置页"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingPage")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.settingLabel = QLabel("Settings", self)
        self.settingLabel.move(60, 63)
        self.personalGroup = SettingCardGroup("Personalization", self.scrollWidget)

        # 应用主题
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            "Application theme",
            "Change the appearance of your application",
            texts=["Light", "Dark", "Use system setting"],
            parent=self.personalGroup,
        )

        # 主题色选择
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FluentIcon.PALETTE,
            "Theme color",
            "Change the theme color of you application",
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

    def __initLayout(self):
        """初始化页面布局"""
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.expandLayout.addWidget(self.personalGroup)

    def __setQss(self):
        """设置自定义样式"""
        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")
        myZJBStyleSheet.SETTING_STYLE.apply(self)

    def __connectSignalToSlot(self):
        """绑定槽函数"""
        cfg.themeChanged.connect(self.__onThemeChanged)
        self.themeColorCard.colorChanged.connect(setThemeColor)

    def __onThemeChanged(self, theme):
        """主题修改槽函数"""
        setTheme(theme)
