from functools import partial
from typing import Any, Callable, Generic, Iterable, TypeVar

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    FluentIcon,
    MessageBoxBase,
    SubtitleLabel,
    TransparentPushButton,
    TransparentToolButton,
)

from zjb.gui.widgets.editor import EditorType

from .editor import Editor

K = TypeVar("K")
V = TypeVar("V")


class DictEditor(Editor, QWidget, Generic[K, V]):
    """字典编辑器, 用于编辑一个字典类型的数据"""

    itemAdded = pyqtSignal(object, object)
    itemRemoved = pyqtSignal(object, object)
    itemChanged = pyqtSignal(object, object)

    def __init__(
        self,
        item_factory: Callable[[], tuple[K, V]],
        editor_factory: Callable[[], EditorType],
        value: dict[K, V] | None = None,
        key2str: Callable[[Any], str] = str,
        can_add=False,
        can_remove=False,
        listen_items=False,
        parent=None,
    ):
        super().__init__(parent=parent)

        self._item_factory = item_factory
        self._editor_factory = editor_factory
        self._key2str = key2str
        self._can_add = can_add
        self._can_remove = can_remove
        self.listen_items = listen_items

        self._value: dict[K, V] = {} if value is None else value

        self._setup_ui()

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.addLayout(self.formLayout)

        for key, _value in self._value.items():
            self._add_row(key, _value)

        if self._can_add:
            self.add_btn = TransparentPushButton("ADD", icon=FluentIcon.ADD)
            self.add_btn.clicked.connect(self._add)
            self.vBoxLayout.addWidget(
                self.add_btn, alignment=Qt.AlignmentFlag.AlignBottom
            )

    def setValue(self, value: dict[K, V]):
        for i in reversed(range(self.formLayout.rowCount())):
            self.formLayout.removeRow(i)
        for key, _value in value.items():
            self._add_row(key, _value)
        self._value = value

    def _add_row(self, key: K, value: V):
        layout = QHBoxLayout()
        editor = self._editor_factory()
        editor.setValue(value)
        editor.valueChanged.connect(partial(self._item_changed, key))
        layout.addWidget(editor)
        if self._can_remove:
            btn = TransparentToolButton(FluentIcon.REMOVE)
            btn.clicked.connect(partial(self._remove, key))
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignTrailing)
        self.formLayout.addRow(BodyLabel(self._key2str(key) + ":"), layout)
        self.updateGeometry()

    def _item_changed(self, key: K, value: V):
        self._value[key] = value
        self.itemChanged.emit(key, value)
        if self.listen_items:
            self.valueChanged.emit(self._value)

    def _add(self):
        key, value = self._item_factory()
        if key in self._value:
            raise KeyError(f"Key {key} already exist in the dict.")
        self._add_row(key, value)
        self._value[key] = value
        self.itemAdded.emit(key, value)
        if self.listen_items:
            self.valueChanged.emit(self._value)

    def _remove(self, key: K):
        index = list(self._value.keys()).index(key)
        self.formLayout.removeRow(index)
        value = self._value.pop(key)
        self.itemRemoved.emit(key, value)
        if self.listen_items:
            self.valueChanged.emit(self._value)

    @property
    def can_add(self):
        return self._can_add

    @can_add.setter
    def can_add(self, can_add: bool):
        if self._can_add == can_add:
            return
        if can_add:
            self.add_btn = TransparentPushButton("ADD", icon=FluentIcon.ADD)
            self.add_btn.clicked.connect(self._add)
            self.vBoxLayout.addWidget(
                self.add_btn, alignment=Qt.AlignmentFlag.AlignBottom
            )
        else:
            self.vBoxLayout.removeWidget(self.add_btn)
            self.add_btn.deleteLater()
        self._can_add = can_add


class KeySetDictEditor(DictEditor[K, V]):
    """用于编辑键属于已知集合的字典数据, 使用下拉框对话框选择键"""

    def __init__(
        self,
        keys: Iterable[K],
        value_factory: Callable[[K], V],
        editor_factory: Callable[[], EditorType],
        value: dict[K, V] | None = None,
        key2str: Callable[[Any], str] = str,
        listen_items=False,
        dialog_parent=None,
        parent=None,
    ):
        super().__init__(
            None,  # type: ignore
            editor_factory,
            value,
            key2str,
            True,
            True,
            listen_items,
            parent,
        )
        self._labels = {key: key2str(key) for key in keys}
        self._value_factory = value_factory
        self._left_keys = [key for key in keys if key not in self._value]
        self._dialog_parent = dialog_parent

    def setValue(self, value: dict[K, V]):
        super().setValue(value)
        # update left keys
        self._left_keys = [key for key in self._labels if key not in self._value]
        if not self._left_keys:
            self.can_add = False

    def _add(self):
        left_labels = [self._labels[key] for key in self._left_keys]
        dialog = ComboBoxDialog(
            left_labels, "Select a key:", self._dialog_parent or self.window()
        )
        if not dialog.exec():
            return
        index = dialog.comboBox.currentIndex()
        key = self._left_keys[index]
        value = self._value_factory(key)

        self._add_row(key, value)
        self._value[key] = value
        self.itemAdded.emit(key, value)
        if self.listen_items:
            self.valueChanged.emit(self._value)

        self._left_keys.pop(index)
        if not self._left_keys:
            self.can_add = False

    def _remove(self, key: K):
        super()._remove(key)
        self._left_keys.append(key)
        self.can_add = True


class ComboBoxDialog(MessageBoxBase):
    def __init__(self, items: Iterable, title: str, parent=None):
        super().__init__(parent)

        self.titleLabel = SubtitleLabel(title)
        self.viewLayout.addWidget(self.titleLabel)

        self.comboBox = ComboBox()
        self.comboBox.addItems(items)
        self.viewLayout.addWidget(self.comboBox)
