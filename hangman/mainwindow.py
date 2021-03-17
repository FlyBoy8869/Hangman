import logging

from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog
from icecream import ic

from . import helpers
from .config import config
from .designerforms import Ui_MainDialog
from .game import Game
from .resultdialog import ResultDialog

ic.configureOutput(includeContext=True)

_image_logo_path = "resources/images/Logo_1.png"
_image_win_path = "resources/images/win.png"
_image_lose_path = "resources/images/lose.jpg"

_alphabet = frozenset("abcdefghijklmnopqrstuvwxyz")


class MainWindow(QDialog, Ui_MainDialog):
    extra = {"classname": "MainWindow"}

    def __init__(self):
        super().__init__()
        self.resize(1000, 785)
        self.setupUi(self)

        self._logger = logging.getLogger("hangman")

        self._ctrl_f = helpers.CtrlKeySequence(Qt.Key_F)
        self._ctrl_n = helpers.CtrlKeySequence(Qt.Key_N)
        self._ctrl_r = helpers.CtrlKeySequence(Qt.Key_R)

        self._game = Game()
        self._game.availableLetters.connect(self.label_available_letters.setText)
        self._game.guessedLettersUpdated.connect(self.label_guessed_letters.setText)
        self._game.imageChanged.connect(self.label_status.setPixmap)
        self._game.maskChanged.connect(self.label_word.setText)
        self._game.gameOver.connect(self._game_over)
        self._game.gameOver.connect(lambda result: self.label_word.setText(self._game.word))

        self._result_dialog = ResultDialog(self)

        self.label_status.setPixmap(QPixmap(_image_logo_path))

        self.pb_new_game.clicked.connect(self._new_game)
        self.pb_show_world.clicked.connect(lambda: print(f"word = {self._game.word}"))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if config.noconfirmexit or helpers.pop_exit_dialog(self):
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

    def _game_over(self, result: str) -> None:
        image_path = _image_win_path if result == "WON" else _image_lose_path
        QTimer.singleShot(0, lambda: self._show_result_dialog(QPixmap(image_path)))

    def _show_result_dialog(self, image: QPixmap) -> None:
        self._result_dialog.run(image)
