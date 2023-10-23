from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import FluentIcon

from zjb.main.api import Surface

from .base_page import BasePage


class SurfacePage(BasePage):
    def __init__(self, surface: Surface, title: str, parent=None):
        super().__init__(surface._gid.str, title, FluentIcon.PHOTO, parent)
        self.surface = surface

        self._setup_ui()

    def _setup_ui(self):
        self.vboxLayout = QVBoxLayout(self)
        self.vboxLayout.addWidget(self.surface.surface_plot())
