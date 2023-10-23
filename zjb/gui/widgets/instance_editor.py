from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Generic, TypeVar

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, ComboBox

from .editor import Editor, EditorType

T = TypeVar("T")


@dataclass
class InstanceEditorAttr:
    name: str
    editor_factory: Callable[[], EditorType]


@dataclass
class InstanceEditorFactory(Generic[T]):
    name: str
    factory: Callable[[], T]
    attrs: list[InstanceEditorAttr]
    is_product: Callable[[T], bool]

    @classmethod
    def from_type(cls, _type: type[T], attrs, name: "str | None" = None):
        if not name:
            name = _type.__name__
        return cls(name, _type, attrs, lambda o: isinstance(o, _type))


class InstanceEditor(Editor, QWidget, Generic[T]):
    factories: list[InstanceEditorFactory[T]] = []

    attrChanged = pyqtSignal(str, object)

    def __init__(self, instance: "T | None" = None, listen_attrs=False, parent=None):
        super().__init__(parent)
        self.listen_attrs = listen_attrs

        self._setup_ui()

        if instance:
            self.setValue(instance)

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)

        self.comboBox = ComboBox()
        self.comboBox.addItems([factory.name for factory in self.factories])
        self.comboBox.currentIndexChanged.connect(self._change_factory)
        self.vBoxLayout.addWidget(self.comboBox)

        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.addLayout(self.formLayout)

    def setValue(self, value: T):
        index = -1
        for i, factory in enumerate(self.factories):
            if factory.is_product(value):
                index = i
                break
        self._instance = value
        self.comboBox.blockSignals(True)
        self.comboBox.setCurrentIndex(index)
        self._update_layout(index)
        self.comboBox.blockSignals(False)

    def _edit_attr(self, attr: InstanceEditorAttr, value):
        setattr(self._instance, attr.name, value)
        self.attrChanged.emit(attr.name, self._instance)
        if self.listen_attrs:
            self.valueChanged.emit(self._instance)

    def _change_factory(self, index: int):
        factory = self.factories[index]
        instance = factory.factory()
        self._instance = instance
        self._update_layout(index)
        self.valueChanged.emit(self._instance)

    def _update_layout(self, index: int):
        for i in reversed(range(self.formLayout.rowCount())):
            self.formLayout.removeRow(i)
        factory = self.factories[index]
        for attr in factory.attrs:
            editor = attr.editor_factory()
            editor.setValue(getattr(self._instance, attr.name))
            editor.valueChanged.connect(partial(self._edit_attr, attr))
            self.formLayout.addRow(BodyLabel(attr.name + ":"), editor)
