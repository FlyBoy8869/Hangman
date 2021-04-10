from enum import IntEnum
from typing import Iterator

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap

from hangman.config import config
from hangman.gameresultdialog import GameResult
from hangman.wordpicker import WordPicker


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
    """Records guessed letters of the Alphabet."""
    def __init__(self):
        self._alphabet = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self._used_letters = ()

    @property
    def used(self):
        return self._used_letters

    @property
    def unused(self) -> tuple[str, ...]:
        return tuple(sorted(self._alphabet.difference(self.used)))

    def record(self, letter: str) -> None:
        """Tracks a letter."""
        if letter not in self.used:
            self._used_letters += letter,

    def has_been_used(self, letter: str) -> bool:
        return letter in self.used


class Mask:
    def __init__(self, word: str):
        self._word = word
        self._mask = ["-"] * len(word)

    @property
    def mask(self):
        return "".join(self._mask)

    def update(self, letter: str) -> None:
        for index, char in enumerate(self._word):
            if char == letter:
                self._mask[index] = letter


class Game(QObject):
    availableLetters = pyqtSignal(str)
    guessedLetters = pyqtSignal(str)
    changeImage = pyqtSignal(QPixmap)
    maskChanged = pyqtSignal(str)
    gameOver = pyqtSignal(GameResult)

    # **********  PUBLIC INTERFACE  ************************************************************************

    def __init__(self):
        super().__init__()

        self._tracker = LetterTracker()

        self._word_to_guess: str
        self._mask: Mask
        self._image_from_genny: Iterator[GallowsImage]
        self._gallows_image: GallowsImage
        self._game_over: bool = False

        self._word_picker = WordPicker()

    @property
    def mask(self) -> str:
        return self._mask.mask

    @property
    def word(self) -> str:
        return self._word_to_guess

    def new_game(self) -> None:
        self._new_game()

    def process_guess(self, letter) -> None:
        if self._game_over or self._tracking(letter, self._tracker):
            return

        self._track(letter, self._tracker)
        self._emit_signal(self.guessedLetters, self._format_guessed_letters_separated_by_spaces())
        self._emit_signal(self.availableLetters, self._format_available_letters_separated_by_spaces())

        if self._letter_in_word(letter, self._word_to_guess):
            self._update_mask(letter)

            if self._did_win(self.mask, self._word_to_guess):
                self._game_over = True
                self._emit_signal(self.gameOver, GameResult.WON)
        else:
            self._process_wrong_guess()

    # **********  PRIVATE  INTERFACE  **********************************************************************

    def _format_available_letters_separated_by_spaces(self) -> str:
        return self._join(self._tracker.unused, " ")

    def _format_guessed_letters_separated_by_spaces(self) -> str:
        return self._join(self._tracker.used, " ")

    def _new_game(self) -> None:
        self._tracker = LetterTracker()
        # self._word_to_guess = self._word_picker.pick_a_word(config.word_count, open(config.word_path))
        self._word_to_guess = self._word_picker(config.word_count, open(config.word_path))
        self._mask = Mask(self._word_to_guess)
        self._image_from_genny = _advance_gallows_image()
        self._gallows_image = next(self._image_from_genny)
        self._game_over = False

        self._emit_signal(self.availableLetters, self._format_available_letters_separated_by_spaces())
        self._emit_signal(self.maskChanged, self.mask)
        self._emit_signal(self.changeImage, self._get_image(GallowsImage.THE_DREADED_GALLOWS))

    def _process_wrong_guess(self) -> None:
        self._gallows_image = next(self._image_from_genny)
        if self._is_game_lost(self._gallows_image, GallowsImage.LEFT_LEG):
            self._emit_signal(self.gameOver, GameResult.LOST)
            self._game_over = True

        self._emit_signal(self.changeImage, self._get_image(self._gallows_image))

    def _update_mask(self, letter: str) -> None:
        self._mask.update(letter)
        self._emit_signal(self.maskChanged, self.mask)

    # **********  PRIVATE INTERFACE - STATIC METHODS  *****************************************************

    @staticmethod
    def _did_win(mask: str, word: str) -> bool:
        return mask == word

    @staticmethod
    def _emit_signal(signal: pyqtSignal, data=None) -> None:
        if data:
            # noinspection PyUnresolvedReferences
            signal.emit(data)
        else:
            # noinspection PyUnresolvedReferences
            signal.emit()

    @staticmethod
    def _get_image(index: GallowsImage) -> QPixmap:
        return QPixmap(_image_paths[index])

    @staticmethod
    def _is_game_lost(image: GallowsImage, losing_criteria: GallowsImage) -> bool:
        return image == losing_criteria

    @staticmethod
    def _join(sequence, separator: str) -> str:
        return separator.join(sequence)

    @staticmethod
    def _letter_in_word(letter: str, word: str) -> bool:
        return letter in word

    @staticmethod
    def _track(letter: str, tracker: LetterTracker) -> None:
        tracker.record(letter)

    @staticmethod
    def _tracking(letter: str, tracker: LetterTracker) -> bool:
        return tracker.has_been_used(letter)
