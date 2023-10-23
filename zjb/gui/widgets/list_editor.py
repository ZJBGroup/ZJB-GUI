from functools import partial
from typing import Callable, Generic, TypeVar

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    Action,
    FluentIcon,
    RoundMenu,
    TransparentPushButton,
    TransparentToolButton,
)

from .editor import Editor, EditorType

T = TypeVar("T")


class ListEditor(Editor, QWidget, Generic[T]):
    itemAdded = pyqtSignal(int, object)
    itemRemoved = pyqtSignal(int)
    itemChanged = pyqtSignal(int, object)

    def __init__(
        self,
        item_factory: Callable[[], T],
        editor_factory: Callable[[], EditorType],
        value: "list[T] | None" = None,
        listen_items=False,
        parent=None,
    ):
        super().__init__(parent)
        self.item_factory = item_factory
        self.editor_factory = editor_factory
        self.listen_item = listen_items

        self._setup_ui()

        self._value: list[T] = []
        if value:
            self.setValue(value)

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)

        self._add_btn()

    def _add_btn(self):
        btn = TransparentPushButton("ADD", icon=FluentIcon.ADD)
        btn.clicked.connect(self._new_item)
        self.vBoxLayout.addWidget(btn)

    def _new_item(self, index: int = 0):
        item = self.item_factory()

        self._clear_row_after(self.vBoxLayout, index)
        self._append_row(index, item)
        for i, v in enumerate(self._value[index:]):
            self._append_row(index + 1 + i, v)

        self._value.insert(index, item)
        self.itemAdded.emit(index, item)
        if self.listen_item:
            self.valueChanged.emit(self._value)

    def _remove_item(self, index: int):
        self._clear_row_after(self.vBoxLayout, index)
        for i, v in enumerate(self._value[index + 1 :]):
            self._append_row(index + i, v)
        if not self._value:
            self._add_btn()

        self._value.pop(index)
        self.itemRemoved.emit(index)
        if self.listen_item:
            self.valueChanged.emit(self._value)

    def _change_item(self, index: int, value):
        self._value[index] = value
        self.itemChanged.emit(index, value)
        if self.listen_item:
            self.valueChanged.emit(self._value)

    def _item_context_menu(self, index: int, btn: QWidget):
        menu = RoundMenu()
        menu.addAction(
            Action(
                FluentIcon.ADD, "Add Before", triggered=partial(self._new_item, index)
            )
        )
        menu.addAction(
            Action(
                FluentIcon.ADD,
                "Add After",
                triggered=partial(self._new_item, index + 1),
            )
        )
        menu.addAction(
            Action(
                FluentIcon.DELETE, "Remove", triggered=partial(self._remove_item, index)
            )
        )
        menu.exec(btn.mapToGlobal(QPoint(-menu.width() + 20, -10)))

    def setValue(self, value: list[T]):
        self._clear_row_after(self.vBoxLayout)

        for i, v in enumerate(value):
            self._append_row(i, v)
        if not value:
            self._add_btn()

        self._value = value

    def _clear_row_after(self, layout: QLayout, index: int = 0):
        while item := layout.takeAt(index):
            if child := item.layout():
                self._clear_row_after(child)
            if widget := item.widget():
                widget.deleteLater()
            del item

    def _append_row(self, index: int, item: T):
        layout = QHBoxLayout()

        editor = self.editor_factory()
        editor.setValue(item)
        editor.valueChanged.connect(lambda v: self._change_item(index, v))

        layout.addWidget(editor)
        btn = TransparentToolButton(FluentIcon.MENU)
        btn.clicked.connect(partial(self._item_context_menu, index, btn))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.insertLayout(index, layout)
