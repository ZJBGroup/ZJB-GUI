from unittest import result

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    LineEdit,
    TransparentPushButton,
    TransparentToolButton,
)


class EditorItem(QWidget):
    itemRemoved = pyqtSignal(QWidget)

    def __init__(
        self,
        keylist,
        parent=None,
    ):
        super().__init__(parent)
        self._keylist = keylist
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 5)

        self.formwidget = QWidget(self)
        self.inputList = QFormLayout(self.formwidget)
        self.inputList.setContentsMargins(0, 0, 0, 0)

        for item in self._keylist:
            self.lineEdit = LineEdit(self)
            self.inputList.addRow(BodyLabel(f"{item}:"), self.lineEdit)

        self.remove_btn = TransparentToolButton(FluentIcon.REMOVE)
        self.remove_btn.clicked.connect(lambda: self.itemRemoved.emit(self))

        self.hBoxLayout.addWidget(self.formwidget)
        self.hBoxLayout.addWidget(self.remove_btn)

    def setBtnDisabled(self, flag: bool):
        self.remove_btn.setDisabled(flag)

    def getValue(self):
        count = self.inputList.rowCount()
        result = []
        for i in range(count):
            item = self.inputList.itemAt(i * 2 + 1).widget()
            result.append(item.text())

        return result[0] if len(result) == 1 else result


class BaseDynamicEditor(QWidget):
    def __init__(
        self,
        keylist,
        parent=None,
    ):
        super().__init__(parent)
        self._keylist = keylist
        self._setup_ui()
        self.add_btn.clicked.connect(self._add)

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout = QFormLayout()
        self.formLayout.setFormAlignment(Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.addLayout(self.formLayout)

        self._add()
        self.add_btn = TransparentPushButton("ADD", icon=FluentIcon.ADD)
        self.add_btn.setFixedWidth(100)

        self.vBoxLayout.addWidget(self.add_btn)

    def _add(self):
        """增加一个条目"""
        self._editor = EditorItem(self._keylist)
        self._editor.itemRemoved.connect(self._remove)
        self.formLayout.addRow(self._editor)

    def _remove(self, widget: EditorItem):
        """移除一个条目"""
        self.formLayout.removeRow(widget)

    def getValue(self):
        """获取所有的数据"""
        count = self.formLayout.rowCount()
        result = []
        for i in range(count):
            item = self.formLayout.itemAt(i)
            result.append(item.widget().getValue())

        return result
