from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QMessageBox, QApplication


def pop_exit_dialog(parent) -> bool:
    return (
        QMessageBox.question(
            parent,
            "Exiting...",
            "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        == QMessageBox.StandardButton.Yes
    )


class Key:
    def __init__(self, key: int):
        self._key = key

    def __eq__(self, other):
        return self._key == other

    def __lt__(self, other):
        return self._key < other

    def __gt__(self, other):
        return self._key > other


class KeySequence:
    # modifier: Qt.KeyboardModifiers = None
    modifier: Qt.KeyboardModifier

    def __init__(self, key: Key):
        self._key = key

    def __eq__(self, other: QKeyEvent):
        assert isinstance(other, QKeyEvent), f"invalid type {type(other)}, must be type <'QKeyEvent'>"
        return self._key == other.key() and QApplication.keyboardModifiers() == self.modifier


class CtrlKeySequence(KeySequence):
    modifier = Qt.KeyboardModifier.ControlModifier
