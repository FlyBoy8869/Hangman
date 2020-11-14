import logging

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog

from . import helpers
from .designerforms import Ui_MainDialog
from .game import Game
from .resultdialog import ResultDialog

_image_paths = [
    "resources/images/gallows-0.png",
    "resources/images/gallows-1.png",
    "resources/images/gallows-2.png",
    "resources/images/gallows-3.png",
    "resources/images/gallows-4.png",
    "resources/images/gallows-5.png",
    "resources/images/gallows-6.png"
]

_letter_A = 65
_letter_Z = 90

_image_logo_path = "resources/images/Logo_1.png"
_image_win_path = "resources/images/win.png"
_image_lose_path = "resources/images/lose.jpg"


class MainWindow(QDialog, Ui_MainDialog):
    extra = {"classname": "MainWindow"}

    def __init__(self, args: dict):
        super().__init__()
        self.resize(1000, 785)
        self.setupUi(self)

        self._logger = logging.getLogger("hangman")

        self._args = args

        self._ctrl_n = helpers.KeySequence(Qt.Key_N, Qt.ControlModifier)
        self._ctrl_r = helpers.KeySequence(Qt.Key_R, Qt.ControlModifier)

        self._game = Game()
        self._game.guessedLettersUpdated.connect(
            lambda guessed_letters: self.label_guessed_letters.setText(guessed_letters)
        )
        self._game.updateProgress.connect(self._update_view)
        self._game.gameOver.connect(self._game_over)

        self._result_dialog = ResultDialog(self)

        self.label_status.setPixmap(QPixmap(_image_logo_path))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._args["noconfirmexit"] or helpers.pop_exit_dialog(self):
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()

        if self._ctrl_n.matches(event):
            self._logger.debug("received CTRL-N", extra=self.extra)
            self._logger.info("requesting new game", extra=self.extra)
            self._new_game()
        elif self._ctrl_r.matches(event):
            self._logger.debug(f"word: {self._game.word}", extra=self.extra)
        elif _letter_A <= key <= _letter_Z:
            self._logger.debug(f"key pressed: '{chr(key)}'", extra=self.extra)
            self._game.process_guess(chr(event.key()))
        else:
            super().keyPressEvent(event)

    def _new_game(self) -> None:
        self.label_status.setPixmap(QPixmap(_image_paths[0]))
        self._game.new_game()

    def _game_over(self, status: tuple[str, str]) -> None:
        result, the_word = status
        image_path = _image_win_path if result == "WON" else _image_lose_path
        QTimer.singleShot(500, lambda: self._show_result_dialog(QPixmap(image_path)))
        self.label_word.setText(the_word)

    def _show_result_dialog(self, image: QPixmap) -> None:
        self._result_dialog.run(image)

    def _update_view(self, state: tuple[int, str, str, str]) -> None:
        progress, available_letters, guessed_letters, mask = state
        self.label_status.setPixmap(QPixmap(_image_paths[progress]))
        self.label_available_letters.setText(available_letters)
        self.label_guessed_letters.setText(guessed_letters)
        self.label_word.setText(mask)
