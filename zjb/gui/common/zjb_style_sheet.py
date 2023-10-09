# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, qconfig

from zjb.gui._rc import find_resource_file


class myZJBStyleSheet(StyleSheetBase, Enum):
    SETTING_STYLE = "setting_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return find_resource_file(f"qss/{theme.value.lower()}/{self.value}.qss")
