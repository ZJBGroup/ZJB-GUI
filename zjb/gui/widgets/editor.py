from typing import Any, Callable

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import LineEdit


class Editor:
    valueChanged = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setValue(self, value):
        raise NotImplementedError


class EditorType(Editor, QWidget):
    """仅用于类型提示"""


class LineEditor(Editor, LineEdit):
    def __init__(
        self,
        value: Any = "",
        _to: Callable[[str], Any] = str,
        _from: Callable[[Any], str] = str,
        parent=None,
    ):
        super().__init__(parent)
        self._from = _from
        self._to = _to
        self.setValue(value)

        self.setClearButtonEnabled(True)
        self.editingFinished.connect(self._commit)

    def setValue(self, value):
        text = self._from(value)
        self.setText(text)
        self._old_text = text

    def _reset(self):
        self.setText(self._old_text)

    def _commit(self):
        text = self.text()
        if text == self._old_text:
            return
        try:
            value = self._to(text)
        except Exception:
            self._reset()
            return
        else:
            self._old_text = text
            self.valueChanged.emit(value)


class FloatEditor(LineEditor):
    def __init__(self, value: float = 0, parent=None):
        super().__init__(value, float, parent=parent)


class IntEditor(LineEditor):
    def __init__(self, value: int = 0, parent=None):
        super().__init__(value, int, parent=parent)
