from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMessageBox, QApplication


def pop_exit_dialog(parent) -> bool:
    if QMessageBox.question(
        parent, "Exiting...", "Are you sure?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    ) == QMessageBox.Yes:
        return True

    return False


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
    modifier: Qt.KeyboardModifiers = None

    def __init__(self, key: Key):
        self._key = key

    def __eq__(self, other: QKeyEvent):
        assert isinstance(other, QKeyEvent), f"invalid type {type(other)}, must be type <'QKeyEvent'>"
        return self._key == other.key() and QApplication.keyboardModifiers() == self.modifier


class CtrlKeySequence(KeySequence):
    modifier = Qt.ControlModifier
