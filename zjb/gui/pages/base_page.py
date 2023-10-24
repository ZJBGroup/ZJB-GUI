# coding:utf-8
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame


class BasePage(QFrame):
    """默认页面"""

    currentPageSignal = pyqtSignal()

    def __init__(self, routeKey: str, title: str, icon, parent=None):
        super().__init__(parent=parent)
        self._tabRouteKey = routeKey
        self._tabTitle = title
        self._tabIcon = icon
        self.setObjectName(routeKey)

    def getRouteKey(self):
        """获取页面对应的 Key"""
        return self._tabRouteKey

    def getTitle(self):
        """获取页面的标题"""
        return self._tabTitle

    def getIcon(self):
        """获取页面的 icon"""
        return self._tabIcon
