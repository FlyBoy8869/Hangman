from enum import IntEnum
from typing import Iterator

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


def _advance_gallows_image() -> Iterator[GallowsImage]:
    yield from GallowsImage


_body = config.body
_image_paths: dict[GallowsImage, str] = {
    GallowsImage.THE_DREADED_GALLOWS: f"resources/images/{_body}/gallows.png",
    GallowsImage.HEAD: f"resources/images/{_body}/head.png",
    GallowsImage.TORSO: f"resources/images/{_body}/torso.png",
    GallowsImage.RIGHT_ARM: f"resources/images/{_body}/leftarm.png",
    GallowsImage.LEFT_ARM: f"resources/images/{_body}/rightarm.png",
    GallowsImage.RIGHT_LEG: f"resources/images/{_body}/rightleg.png",
    GallowsImage.LEFT_LEG: f"resources/images/{_body}/leftleg.png"
}


class LetterTracker:
    """Tracks letters guessed and letters remaining from the Alphabet."""
    def __init__(self):
        self._available_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._guessed_letters = []

    @property
    def available_letters(self):
        return self._available_letters

    @property
    def guessed_letters(self):
        return self._guessed_letters

    def track_it(self, letter: str) -> bool:
        """Returns True if letter already tracked, False otherwise."""
        if letter not in self._guessed_letters:
            self._track(letter)
            self._remove_from_available_letters(letter)
            return False
        return True

    def _track(self, letter: str):
        self._guessed_letters.append(letter)

    def _remove_from_available_letters(self, letter: str) -> None:
        self._available_letters = self._available_letters.replace(letter, "")


class GuessProcessor:
    def __init__(self, word: str):
        self._word = word
        self._letter_tracker = LetterTracker()
        self._remaining_guesses = 6

    def process(self, letter: str):
        if self._tracked(letter):
            return

        return self._have_any_guesses_left()

    def _tracked(self, letter: str) -> bool:
        return self._letter_tracker.track_it(letter)

    def _have_any_guesses_left(self):
        self._remaining_guesses -= 1
        return self._remaining_guesses


class Game(QObject):
    availableLetters = pyqtSignal(str)
    guessedLettersUpdated = pyqtSignal(str)
    changeImage = pyqtSignal(QPixmap)
    maskChanged = pyqtSignal(str)
    gameOver = pyqtSignal(GameResult)

    # **********  PUBLIC INTERFACE  ************************************************************************

    def __init__(self):
        super().__init__()

        self._word_picker = WordPicker()
        self._word_picker.publish_word.connect(self._received_new_word)

        self._letter_tracker = LetterTracker()

        self._word_to_guess: str
        self._mask: list
        self._image_from_genny: Iterator[GallowsImage]
        self._current_image: GallowsImage
        self._game_over: bool = False

        if config.range:
            if len(config.range) > 1:
                self._word_picker.add_filter(RangeFilter(config.range))
            else:
                self._word_picker.add_filter(LengthFilter(config.range[0]))

    @property
    def mask(self) -> str:
        return self._join(self._mask, "")

    @property
    def word(self) -> str:
        return self._word_to_guess

    def new_game(self) -> None:
        self._word_picker.pick_a_word()

    def _received_new_word(self, word: str):
        QTimer.singleShot(_spinner_delay, lambda: self._new_game(word))

    def _new_game(self, word: str) -> None:
        self._letter_tracker = LetterTracker()
        self._word_to_guess = word
        self._mask = ["-"] * len(self._word_to_guess)
        self._image_from_genny = _advance_gallows_image()
        self._current_image = next(self._image_from_genny)
        self._game_over = False

        self._emit_available_letters()
        self._emit_mask_changed()
        self._emit_change_image(GallowsImage.THE_DREADED_GALLOWS)

    def process_guess(self, letter) -> None:
        if self._game_over or self._letter_tracker.track_it(letter):
            return

        self._emit_guessed_letters()
        self._emit_available_letters()

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
        self._current_image = next(self._image_from_genny)
        return self._current_image == GallowsImage.LEFT_LEG

    def _process_wrong_guess(self):
        if self._is_game_lost():
            # noinspection PyUnresolvedReferences
            self.gameOver.emit(GameResult.LOST)
            self._game_over = True

        # noinspection PyUnresolvedReferences
        self._emit_change_image(self._current_image)

    def _emit_available_letters(self):
        # noinspection PyUnresolvedReferences
        self.availableLetters.emit(self._get_available_letters())

    def _emit_guessed_letters(self):
        # noinspection PyUnresolvedReferences
        self.guessedLettersUpdated.emit(self._get_guessed_letters())

    def _emit_change_image(self, index: GallowsImage):
        # noinspection PyUnresolvedReferences
        self.changeImage.emit(QPixmap(_image_paths[index]))

    def _emit_mask_changed(self):
        # noinspection PyUnresolvedReferences
        self.maskChanged.emit(self.mask)

    def _get_available_letters(self):
        return self._join(self._letter_tracker.available_letters, " ")

    def _get_guessed_letters(self):
        return self._join(self._letter_tracker.guessed_letters, " ")

    def _update_mask(self, letter: str) -> None:
        indexes = [
            index
            for index, char in enumerate(self._word_to_guess)
            if letter == char
        ]

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
