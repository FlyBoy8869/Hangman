from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMessageBox


def pop_exit_dialog(parent) -> bool:
    if QMessageBox.question(
        parent, "Exiting...", "Are you sure?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    ) == QMessageBox.Yes:
        return True

    return False


class KeySequence:
    def __init__(self, key: Qt.Key, modifiers: Qt.KeyboardModifiers):
        assert Qt.Key_A <= key <= Qt.Key_Z, "Key must be in range 'A' - 'Z'"
        self._key = key
        self._modifiers = modifiers

    def matches(self, event: QKeyEvent):
        assert isinstance(event, QKeyEvent), "event must be an instance of QKeyEvent"
        return self._key == event.key() and event.modifiers() == self._modifiers
