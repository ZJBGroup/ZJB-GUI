from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QFocusEvent
from qfluentwidgets import LineEdit


class Editor():

    valueChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__()

    def setValue(self, value):
        raise NotImplementedError


class LineEditor(Editor, LineEdit):

    def __init__(self, parent=None, _eval=None):
        super().__init__(parent)

        self.setClearButtonEnabled(True)
        self.textEdited.connect(self._on_text_edited)
        self.returnPressed.connect(self._commit)
        self.installEventFilter(self)

        self.setEval(_eval)
        self._value = None
        self._edited_flag = False

    def setValue(self, value):
        self._value = value
        self.setText(str(value))

    def setEval(self, _eval):
        self._eval = _eval

    def _on_text_edited(self):
        self._edited_flag = True

    def eventFilter(self, obj: LineEdit, e: QEvent) -> bool:
        if isinstance(e, QFocusEvent) and e.lostFocus():
            if e.reason() in (Qt.FocusReason.MouseFocusReason, Qt.FocusReason.TabFocusReason):
                if self._edited_flag:
                    self._commit()
        return super().eventFilter(obj, e)

    def _update(self):
        self.setText(str(self._value))

    def _commit(self):
        value = self.text()
        if not value:
            self._update()
            return
        if self._eval:
            try:
                value = self._eval(value)
            except Exception:
                self._update()
                return
        self.valueChanged.emit(value)
        self.clearFocus()


class FloatEditor(LineEditor):

    def __init__(self, parent=None):
        super().__init__(parent, float)
