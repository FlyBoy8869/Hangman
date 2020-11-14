import logging
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal

from hangman.wordgenerator import WordSelector


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

        self._word_selector = WordSelector(Path("hangman/words.txt"))
        self._guessed_letters = []
        self._available_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._word_to_guess = None
        self._game_over = True
        self._progress = 0
        self._mask = []

    def get_word(self) -> str:
        return self._word_to_guess

    def new_game(self) -> None:
        self._logger.info("Initializing new game state", extra=self.extra)
        self._word_to_guess = self._word_selector.select()
        self._mask = ["-"] * len(self._word_to_guess)
        self._available_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._guessed_letters = []
        self._game_over = False
        self._progress = 0

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
                self.gameOver.emit(("WON", self._word_to_guess))
        else:
            self._do_wrong_guess()

    # **********  PRIVATE  INTERFACE  **********************************************************************

    def _did_win(self) -> bool:
        return self._get_mask() == self._word_to_guess

    def _is_game_lost(self):
        self._progress += 1
        return self._progress == 6

    def _do_wrong_guess(self):
        if self._is_game_lost():
            self._emit_progress_update()
            self.gameOver.emit(("LOST", self._word_to_guess))
            self._game_over = True
        else:
            self._emit_progress_update()

    def _emit_progress_update(self):
        self.updateProgress.emit(
            (self._progress, self._get_available_letters(), self._get_guessed_letters(), self._get_mask())
        )

    def _get_available_letters(self):
        return self._join(self._available_letters, " ")

    def _get_guessed_letters(self):
        return self._join(self._guessed_letters, " ")

    def _get_mask(self):
        return self._join(self._mask, "")

    def _record_letter(self, letter: str) -> None:
        self._guessed_letters.append(letter)
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
