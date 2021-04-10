import random
from typing import IO

from hangman.filters import FilterCollection


class WordPicker:
    def __init__(self, selection_filters: FilterCollection = None):
        self._filters = selection_filters

    def __call__(self, word_count: int, file: IO[str]) -> str:
        while self._is_filtered_out(
                    word := self._get_word_from_file(
                            at_index=self._get_index(word_count),
                            iterator=enumerate(file))):
            file.seek(0)

        file.close()
        return word.strip().upper()

    def _is_filtered_out(self, word: str) -> bool:
        return not (not self._filters or self._filters.apply(word))

    @staticmethod
    def _get_index(upper_limit: int) -> int:
        return random.randrange(upper_limit)

    @staticmethod
    def _get_word_from_file(*, at_index: int, iterator):
        for _ in range(at_index):
            next(iterator)
        return next(iterator)[1]
