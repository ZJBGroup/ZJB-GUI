import os
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import FluentIcon, TransparentToolButton

from .editor import LineEditor


class OpenFileEditor(LineEditor):
    def __init__(self, value: Any = "", directory="", filter="", parent=None):
        super().__init__(value, self._validate, parent=parent)

        self.caption = "Open File"
        self.directory = directory
        self.filter = filter

        self.btn_dialog = TransparentToolButton(FluentIcon.FOLDER)
        self.btn_dialog.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dialog.setFixedSize(29, 25)
        self.btn_dialog.clicked.connect(self._dialog)
        self.hBoxLayout.addWidget(self.btn_dialog)

        self.setTextMargins(0, 0, 56, 0)

    def _validate(self, text: str):
        if not os.path.exists(text):
            raise FileNotFoundError(f"{text} not exists")
        return text

    def _dialog(self):
        name, _ = QFileDialog.getOpenFileName(
            self.window(), self.caption, self.directory, filter=self.filter
        )
        if name:
            self.setValue(name)
            self.valueChanged.emit(name)
