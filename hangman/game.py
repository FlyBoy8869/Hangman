import logging
from enum import IntEnum
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap

from hangman.config import config
from hangman.wordlist import LengthFilter, WordList


class GallowsImage(IntEnum):
    THE_DREADED_GALLOWS = 0
    HEAD = 1
    TORSO = 2
    LEFT_ARM = 3
    RIGHT_ARM = 4
    RIGHT_LEG = 5
    LEFT_LEG = 6


_body = config.body
_image_paths = {
    GallowsImage.THE_DREADED_GALLOWS: f"resources/images/{_body}/gallows.png",
    GallowsImage.HEAD: f"resources/images/{_body}/head.png",
    GallowsImage.TORSO: f"resources/images/{_body}/torso.png",
    GallowsImage.RIGHT_ARM: f"resources/images/{_body}/leftarm.png",
    GallowsImage.LEFT_ARM: f"resources/images/{_body}/rightarm.png",
    GallowsImage.RIGHT_LEG: f"resources/images/{_body}/rightleg.png",
    GallowsImage.LEFT_LEG: f"resources/images/{_body}/leftleg.png"
}


def _advance_gallows_image():
    for image in GallowsImage:
        yield image


class Game(QObject):
    availableLetters = pyqtSignal(str)
    guessedLettersUpdated = pyqtSignal(str)
    imageChanged = pyqtSignal(QPixmap)
    maskChanged = pyqtSignal(str)
    gameOver = pyqtSignal(str)
    gameWon = pyqtSignal(str)

    extra = {"classname": "Game"}

    # **********  PUBLIC INTERFACE  ************************************************************************

    def __init__(self):
        super().__init__()

        self._logger = logging.getLogger("hangman")

        self._word_list = WordList.create_from_file(Path("hangman/words.txt"))
        if config.length and config.length > 0:
            word_length = LengthFilter(config.length)
            self._word_list.add_filter(word_length)
        self._guessed_letters = []
        self._available_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._word_to_guess = None
        self._game_over = True
        self._game_state = None
        self._current_image = None
        self._mask = []

    @property
    def mask(self) -> str:
        return self._join(self._mask, "")

    @property
    def word(self) -> str:
        return self._word_to_guess

    def new_game(self) -> None:
        self._logger.info("Initializing new game state", extra=self.extra)
        self._word_to_guess = self._word_list.pick_a_word()
        self._mask = ["-"] * len(self._word_to_guess)
        self._available_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._guessed_letters = []
        self._game_over = False
        self._game_state = _advance_gallows_image()
        self._current_image = next(self._game_state)

        # noinspection PyUnresolvedReferences
        self.maskChanged.emit(self.mask)
        # noinspection PyUnresolvedReferences
        self._emit_image_changed(GallowsImage.THE_DREADED_GALLOWS)

    def process_guess(self, letter) -> None:
        self._logger.info(f"processing guess: '{letter}'", extra=self.extra)

        if self._game_over or letter in self._guessed_letters:
            return

        self._record_letter(letter)
        self._remove_letter_choice(letter)

        if self._word_contains_letter(letter):
            self._update_mask(letter)

            if self._did_win():
                self._game_over = True
                # noinspection PyUnresolvedReferences
                self.gameOver.emit("WON")
        else:
            self._process_wrong_guess()

    # **********  PRIVATE  INTERFACE  **********************************************************************

    def _did_win(self) -> bool:
        return self.mask == self._word_to_guess

    def _is_game_lost(self):
        self._current_image: GallowsImage = next(self._game_state)
        return self._current_image == GallowsImage.LEFT_LEG

    def _process_wrong_guess(self):
        if self._is_game_lost():
            # noinspection PyUnresolvedReferences
            self.gameOver.emit("LOST")
            self._game_over = True

        # noinspection PyUnresolvedReferences
        self._emit_image_changed(self._current_image)

    def _emit_image_changed(self, index: GallowsImage):
        # noinspection PyUnresolvedReferences
        self.imageChanged.emit(QPixmap(_image_paths[index]))

    def _get_available_letters(self):
        return self._join(self._available_letters, " ")

    def _get_guessed_letters(self):
        return self._join(self._guessed_letters, " ")

    def _record_letter(self, letter: str) -> None:
        self._guessed_letters.append(letter)
        # noinspection PyUnresolvedReferences
        self.guessedLettersUpdated.emit(self._get_guessed_letters())

    def _remove_letter_choice(self, letter) -> None:
        self._available_letters = self._available_letters.replace(letter, "")
        # noinspection PyUnresolvedReferences
        self.availableLetters.emit(self._get_available_letters())

    def _update_mask(self, letter: str) -> None:
        indexes = []
        for index, char in enumerate(self._word_to_guess):
            if letter == char:
                indexes.append(index)

        for index in indexes:
            self._mask[index] = letter

        # noinspection PyUnresolvedReferences
        self.maskChanged.emit(self.mask)

    def _word_contains_letter(self, letter: str) -> bool:
        return letter in self._word_to_guess

    # **********  PRIVATE INTERFACE - STATIC METHODS  *****************************************************

    @staticmethod
    def _join(sequence, separator: str):
        return separator.join(sequence)
