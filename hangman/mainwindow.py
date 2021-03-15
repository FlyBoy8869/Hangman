import logging

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog
from icecream import ic

from . import helpers
from .designerforms import Ui_MainDialog
from .game import Game, GameState
from .resultdialog import ResultDialog

ic.configureOutput(includeContext=True)

_image_paths = {
    GameState.GALLOWS: "resources/images/gallows-0.png",
    GameState.HEAD: "resources/images/gallows-1.png",
    GameState.TORSO: "resources/images/gallows-2.png",
    GameState.LEFT_ARM: "resources/images/gallows-3.png",
    GameState.RIGHT_ARM: "resources/images/gallows-4.png",
    GameState.RIGHT_LEG: "resources/images/gallows-5.png",
    GameState.LEFT_LEG: "resources/images/gallows-6.png"
}

_image_logo_path = "resources/images/Logo_1.png"
_image_win_path = "resources/images/win.png"
_image_lose_path = "resources/images/lose.jpg"

_alphabet = frozenset("abcdefghijklmnopqrstuvwxyz")


class MainWindow(QDialog, Ui_MainDialog):
    extra = {"classname": "MainWindow"}

    def __init__(self, args: dict):
        super().__init__()
        self.resize(1000, 785)
        self.setupUi(self)

        self._logger = logging.getLogger("hangman")

        self._args = args

        self._ctrl_f = helpers.CtrlKeySequence(Qt.Key_F)
        self._ctrl_n = helpers.CtrlKeySequence(Qt.Key_N)
        self._ctrl_r = helpers.CtrlKeySequence(Qt.Key_R)

        self._game = Game()
        self._game.guessedLettersUpdated.connect(
            lambda guessed_letters: self.label_guessed_letters.setText(guessed_letters)
        )
        self._game.updateProgress.connect(self._update_view)
        self._game.gameOver.connect(self._game_over)

        self._result_dialog = ResultDialog(self)

        self.label_status.setPixmap(QPixmap(_image_logo_path))

        self.pb_new_game.clicked.connect(self._new_game)
        self.pb_show_world.clicked.connect(lambda: print(f"word = {self._game.word}"))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._args["noconfirmexit"] or helpers.pop_exit_dialog(self):
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event == self._ctrl_n:
            self._logger.debug("received CTRL-N", extra=self.extra)
            self._logger.info("requesting new game", extra=self.extra)
            self._new_game()
        elif event == self._ctrl_r:
            self._logger.debug(f"word: {self._game.word}", extra=self.extra)
        elif event == self._ctrl_f:
            ic("select filters to apply to the word list")
        elif event.text() in _alphabet:
            key = chr(event.key())
            self._logger.debug(f"key pressed: '{key}'", extra=self.extra)
            self._game.process_guess(key)
        else:
            super().keyPressEvent(event)

    def _new_game(self) -> None:
        self._game.new_game()

    def _game_over(self, status: tuple[str, str]) -> None:
        result, the_word = status
        image_path = _image_win_path if result == "WON" else _image_lose_path
        QTimer.singleShot(500, lambda: self._show_result_dialog(QPixmap(image_path)))
        self.label_word.setText(the_word)

    def _show_result_dialog(self, image: QPixmap) -> None:
        self._result_dialog.run(image)

    def _update_view(self, state: tuple[GameState, str, str, str]) -> None:
        image, available_letters, guessed_letters, mask = state
        self.label_status.setPixmap(QPixmap(_image_paths[image]))
        self._logger.debug(f"setting image to {image.name}", extra=self.extra)
        self.label_available_letters.setText(available_letters)
        self.label_guessed_letters.setText(guessed_letters)
        self.label_word.setText(mask)
