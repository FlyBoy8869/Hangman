import random
from typing import IO

import attr

from hangman.filters import FilterCollection


@attr.s(auto_attribs=True)
class WordPicker:
    _selection_filters: FilterCollection = None

    def __call__(self, word_count: int, file: IO[str]) -> str:
        while True:
            word = self._get_word_from_file_at_index(
                file=file,
                index=random.randrange(word_count)
            )
            if self._word_passes_filters(word):
                file.close()
                return word.upper()

            file.seek(0)  # word rejected, rewind and try again

    def _word_passes_filters(self, word: str) -> bool:
        return not self._selection_filters or self._selection_filters.apply(word)

    @staticmethod
    def _get_word_from_file_at_index(*, file: IO[str], index: int) -> str:
        for _ in range(index):
            file.readline()
        return file.readline().strip()
