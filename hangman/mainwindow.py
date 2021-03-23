import logging

from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QMovie, QPalette, QPixmap
from PyQt5.QtWidgets import QDialog

from . import helpers
from .config import config
from hangman import hm
from .designerforms import Ui_MainDialog
from .game import Game
from .resultdialog import ResultDialog


class SuccessDialog:
    def __init__(self, parent=None):
        self._dialog = ResultDialog(parent)

    def show(self, result) -> None:
        self._change_palette(result)
        self._dialog.run(self._get_image(result))

    def _change_palette(self, result) -> None:
        palette = QPalette()
        color = QColor(*hm.orange_shade)

        if result != "WON":
            color = Qt.red

        palette.setBrush(QPalette.Window, color)
        self._dialog.setPalette(palette)

    def _get_image(self, result) -> QPixmap:
        image = hm.image_win_path
        if result != "WON":
            image = hm.image_lose_path

        return QPixmap(image)


class MainWindow(QDialog, Ui_MainDialog):
    extra = {"classname": "MainWindow"}
    window_size = (1000, 785)
    spinner_speed = 500

    def __init__(self):
        super().__init__()
        self.resize(*self.window_size)
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

        # self._result_dialog = ResultDialog(self)
        self._result_dialog = SuccessDialog(self)

        self.label_status.setPixmap(QPixmap(hm.image_logo_path))

        self.pb_new_game.clicked.connect(self._new_game)
        self.pb_show_world.clicked.connect(lambda: print(f"word = {self._game.word}"))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if config.noconfirmexit or helpers.pop_exit_dialog(self):
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event == self._ctrl_n:
            self._new_game()
        elif event == self._ctrl_r:
            ic(self._game.word)
        elif event == self._ctrl_f:
            ic("select filters to apply to the word list")
        elif event.text() in hm.alphabet:
            key = chr(event.key())
            ic(key)
            self._game.process_guess(key)
        else:
            super().keyPressEvent(event)

    def _new_game(self) -> None:
        self.label_word.clear()
        self.label_available_letters.clear()
        self.label_guessed_letters.clear()
        self._show_spinner()
        self._game.new_game()

    def _game_over(self, result: str) -> None:
        QTimer.singleShot(0, lambda: self._show_result_dialog(result))

    def _show_result_dialog(self, result) -> None:
        self._result_dialog.show(result)

    def _show_spinner(self):
        movie = QMovie(hm.spinner)
        movie.setSpeed(self.spinner_speed)
        self.label_status.setMovie(movie)
        movie.start()
