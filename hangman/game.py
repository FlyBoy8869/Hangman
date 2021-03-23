from enum import IntEnum

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap

from hangman.config import config
from hangman.filters import LengthFilter, RangeFilter
from hangman.gameresultdialog import GameResult
from hangman.wordpicker import WordPicker

_spinner_delay: int = 700


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
    gameOver = pyqtSignal(GameResult)

    # **********  PUBLIC INTERFACE  ************************************************************************

    def __init__(self):
        super().__init__()

        self._word_picker = WordPicker()
        self._word_picker.publish_word.connect(self._received_new_word)
        if config.range and len(config.range) > 1:
            self._word_picker.add_filter(RangeFilter(config.range))
        elif config.range:
            self._word_picker.add_filter(LengthFilter(config.range[0]))
        self._guessed_letters = []
        self._word_to_guess = None
        self._game_over = True
        self._image_from_genny = None
        self._current_image = None
        self._mask = []

    @property
    def mask(self) -> str:
        return self._join(self._mask, "")

    @property
    def word(self) -> str:
        return self._word_to_guess

    def new_game(self) -> None:
        self._word_picker.pick_a_word()

    def _received_new_word(self, word: str):
        self._word_to_guess = word
        QTimer.singleShot(_spinner_delay, self._new_game)

    def _new_game(self) -> None:
        self._mask = ["-"] * len(self._word_to_guess)
        self._available_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._guessed_letters = []
        self._game_over = False
        self._image_from_genny = _advance_gallows_image()
        self._current_image = next(self._image_from_genny)

        self._emit_available_letters()
        # noinspection PyUnresolvedReferences
        self._emit_mask_changed()
        # noinspection PyUnresolvedReferences
        self._emit_image_changed(GallowsImage.THE_DREADED_GALLOWS)

    def process_guess(self, letter) -> None:
        if self._game_over or letter in self._guessed_letters:
            return

        self._record_letter(letter)
        self._remove_letter_choice(letter)

        if self._letter_in_word(letter):
            self._update_mask(letter)

            if self._did_win():
                self._game_over = True
                # noinspection PyUnresolvedReferences
                self.gameOver.emit(GameResult.WON)
        else:
            self._process_wrong_guess()

    # **********  PRIVATE  INTERFACE  **********************************************************************

    def _did_win(self) -> bool:
        return self.mask == self._word_to_guess

    def _is_game_lost(self):
        self._current_image: GallowsImage = next(self._image_from_genny)
        return self._current_image == GallowsImage.LEFT_LEG

    def _process_wrong_guess(self):
        if self._is_game_lost():
            # noinspection PyUnresolvedReferences
            self.gameOver.emit(GameResult.LOST)
            self._game_over = True

        # noinspection PyUnresolvedReferences
        self._emit_image_changed(self._current_image)

    def _emit_available_letters(self):
        # noinspection PyUnresolvedReferences
        self.availableLetters.emit(self._get_available_letters())

    def _emit_image_changed(self, index: GallowsImage):
        # noinspection PyUnresolvedReferences
        self.imageChanged.emit(QPixmap(_image_paths[index]))

    def _emit_mask_changed(self):
        # noinspection PyUnresolvedReferences
        self.maskChanged.emit(self.mask)

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
        self._emit_available_letters()

    def _update_mask(self, letter: str) -> None:
        indexes = []
        for index, char in enumerate(self._word_to_guess):
            if letter == char:
                indexes.append(index)

        for index in indexes:
            self._mask[index] = letter

        # noinspection PyUnresolvedReferences
        self._emit_mask_changed()

    def _letter_in_word(self, letter: str) -> bool:
        return letter in self._word_to_guess

    # **********  PRIVATE INTERFACE - STATIC METHODS  *****************************************************

    @staticmethod
    def _join(sequence, separator: str):
        return separator.join(sequence)
