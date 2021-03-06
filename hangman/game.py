import logging
from enum import IntEnum
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal

from hangman.wordlist import WordList


class GameState(IntEnum):
    GALLOWS = 0
    HEAD = 1
    TORSO = 2
    LEFT_ARM = 3
    RIGHT_ARM = 4
    RIGHT_LEG = 5
    LEFT_LEG = 6


def _advance_game_state():
    for state in GameState:
        yield state


class Game(QObject):
    guessedLettersUpdated = pyqtSignal(str)
    updateProgress = pyqtSignal(tuple)
    gameOver = pyqtSignal(tuple)
    gameWon = pyqtSignal(str)

    extra = {"classname": "Game"}

    # **********  PUBLIC INTERFACE  ************************************************************************

    def __init__(self):
        super().__init__()

        self._logger = logging.getLogger("hangman")

        self._word_list = WordList.create_from_file(Path("hangman/words.txt"))
        self._guessed_letters = []
        self._available_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._word_to_guess = None
        self._game_over = True
        self._game_state = None
        self._current_state = None
        self._mask = []

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
        self._game_state = _advance_game_state()
        self._current_state = next(self._game_state)
        self._emit_progress_update()

    def process_guess(self, letter) -> None:
        self._logger.info(f"processing guess: '{letter}'", extra=self.extra)
        if self._game_over or letter in self._guessed_letters:
            return

        self._record_letter(letter)
        self._remove_letter_choice(letter)

        if self._word_contains_letter(letter):
            self._reveal_guess(letter)
            self._emit_progress_update()

            if self._did_win():
                self._game_over = True
                # noinspection PyUnresolvedReferences
                self.gameOver.emit(("WON", self._word_to_guess))
        else:
            self._do_wrong_guess()

    # **********  PRIVATE  INTERFACE  **********************************************************************

    def _did_win(self) -> bool:
        return self._get_mask() == self._word_to_guess

    def _is_game_lost(self):
        self._current_state: GameState = next(self._game_state)
        return self._current_state.value == 6

    def _do_wrong_guess(self):
        if self._is_game_lost():
            self._emit_progress_update()
            # noinspection PyUnresolvedReferences
            self.gameOver.emit(("LOST", self._word_to_guess))
            self._game_over = True
        else:
            self._emit_progress_update()

    def _emit_progress_update(self):
        # noinspection PyUnresolvedReferences
        self.updateProgress.emit(
            (
                self._current_state,
                self._get_available_letters(),
                self._get_guessed_letters(),
                self._get_mask()
            )
        )

    def _get_available_letters(self):
        return self._join(self._available_letters, " ")

    def _get_guessed_letters(self):
        return self._join(self._guessed_letters, " ")

    def _get_mask(self):
        return self._join(self._mask, "")

    def _record_letter(self, letter: str) -> None:
        self._guessed_letters.append(letter)
        # noinspection PyUnresolvedReferences
        self.guessedLettersUpdated.emit(self._get_guessed_letters())

    def _remove_letter_choice(self, letter) -> None:
        self._available_letters = self._available_letters.replace(letter, "")

    def _reveal_guess(self, letter: str) -> None:
        indexes = []
        for index, char in enumerate(self._word_to_guess):
            if letter == char:
                indexes.append(index)

        for index in indexes:
            self._mask[index] = letter

    def _word_contains_letter(self, letter: str) -> bool:
        return letter in self._word_to_guess

    # **********  PRIVATE INTERFACE - STATIC METHODS  *****************************************************

    @staticmethod
    def _join(sequence, separator: str):
        return separator.join(sequence)
