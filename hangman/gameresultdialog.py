from enum import Enum

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.QtWidgets import QDialog

from .designerforms import Ui_ResultDialog


class GameResult(Enum):
    WON = 1
    LOST = 2


class GameResultDialog(QDialog, Ui_ResultDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        self.accept()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.accept()

    def set_pixmap(self, image: QPixmap):
        self.label_result.setPixmap(image)


_image_win_path = "resources/images/win.png"
_image_lose_path = "resources/images/lose.png"

_image_paths = {
    GameResult.WON: _image_win_path,
    GameResult.LOST: _image_lose_path
}

# rgba
_orange_shade = (240, 139, 69, 255)
_pink_shade = (215, 26, 90, 255)

_dialog_window_color = {
    GameResult.WON: QColor(*_orange_shade),
    GameResult.LOST: Qt.red
}


class GameResultDialogWrapper:
    def __init__(self, *, parent=None):
        self._dialog = GameResultDialog(parent)

    def exec(self, result: GameResult) -> None:
        self._dialog.setPalette(self._create_palette_from(result))
        self._dialog.set_pixmap(self._create_image_from(result))
        self._dialog.exec()

    @staticmethod
    def _create_palette_from(result: GameResult) -> QPalette:
        palette = QPalette()
        color = _dialog_window_color[result]
        palette.setBrush(QPalette.Window, color)
        return palette

    @staticmethod
    def _create_image_from(result: GameResult) -> QPixmap:
        return QPixmap(_image_paths[result])
