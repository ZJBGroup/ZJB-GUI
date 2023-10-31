from qfluentwidgets import FluentIcon

from .base_page import BasePage


class AnalysisPage(BasePage):
    def __init__(self, data):
        super().__init__(data._gid.str + "Analysis", "Analysis", FluentIcon.DOCUMENT)
        self.data = data

        self._setup_ui()

        self.setObjectName(data._gid.str + "Analysis")

    def _setup_ui(self):
        pass
