import random
from typing import IO

from PyQt5.QtCore import QObject

from hangman.filters import FilterCollection


class WordPicker(QObject):
    def __init__(self, word_count: int, file: IO[str], selection_filters: FilterCollection = None):
        super().__init__()
        self._word_count = word_count
        self._file_obj = file
        self._filters = selection_filters

    def set_filters(self, filters: FilterCollection):
        self._filters = filters

    def pick_a_word(self):
        while True:
            word = self._get_word_from_file(
                at_index=self._get_index(self._word_count),
                file=self._file_obj
            )
            if word and not self._filters:
                break
            if self._filters.apply(word):
                break

            self._file_obj.seek(0)

        self._file_obj.close()
        return word.upper()

    @staticmethod
    def _get_index(upper_limit: int) -> int:
        return random.randrange(0, upper_limit)

    @staticmethod
    def _get_word_from_file(at_index: int, file: IO[str]) -> str:
        for index, word in enumerate(file):
            if at_index == index:
                return word.strip()
