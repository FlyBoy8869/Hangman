from PyQt6 import QtGui
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QDialog

from . import helpers
from .config import config
from .designerforms import Ui_MainDialog
from .filters import dummy_filter_collection
from .game import Game, LetterTracker
from .gameresultdialog import GameResult, GameResultDialogWrapper
from .wordpicker import WordPicker

_alphabet = frozenset("abcdefghijklmnopqrstuvwxyz")

_image_logo_path = "resources/images/Logo_1.png"
_spinner = "resources/images/spinners/spinner.gif"

_spinner_delay: int = 700


class MainWindow(QDialog, Ui_MainDialog):
    extra = {"classname": "MainWindow"}
    window_size = (1000, 785)
    spinner_speed = 500

    def __init__(self):
        super().__init__()
        self.resize(*self.window_size)
        self.setupUi(self)

        self._ctrl_f = helpers.CtrlKeySequence(Qt.Key.Key_F)
        self._ctrl_n = helpers.CtrlKeySequence(Qt.Key.Key_N)
        self._ctrl_r = helpers.CtrlKeySequence(Qt.Key.Key_R)

        self._file_obj = open(config.word_path)
        word_picker = WordPicker(self._file_obj, config.word_count, dummy_filter_collection)

        self._game = Game(word_picker, LetterTracker())
        self._game.availableLetters.connect(self.label_available_letters.setText)
        self._game.guessedLetters.connect(self.label_guessed_letters.setText)
        self._game.changeImage.connect(self.label_status.setPixmap)
        self._game.maskChanged.connect(self.label_word.setText)
        self._game.gameOver.connect(self._game_over)
        self._game.gameOver.connect(lambda result: self.label_word.setText(self._game.word))

        self._result_dialog = GameResultDialogWrapper(parent=self)

        self.label_status.setPixmap(QPixmap(_image_logo_path))

        self.pb_new_game.clicked.connect(self._new_game)
        self.pb_show_world.clicked.connect(lambda: print(f"word = {self._game.word}"))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if config.noconfirmexit or helpers.pop_exit_dialog(self):
            self._file_obj.close()
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
        elif event.text() in _alphabet:
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
        QTimer.singleShot(_spinner_delay, self._game.new_game)

    def _game_over(self, result: GameResult) -> None:
        # QTimer is used to allow the last letter guessed to show up immediately
        QTimer.singleShot(0, lambda: self._result_dialog.exec(result))

    def _show_spinner(self):
        movie = QMovie(_spinner)
        movie.setSpeed(self.spinner_speed)
        self.label_status.setMovie(movie)
        movie.start()
