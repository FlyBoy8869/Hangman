import random
from typing import IO

import attr

from hangman.filters import FilterCollection


@attr.s(auto_attribs=True)
class WordPicker:
    _file: IO[str]
    _file_length: int
    _filters: FilterCollection

    def pick(self) -> str:
        while self._word_filtered_out(word := self._get_word_from_file()):
            continue
        return word.strip().upper()

    def _word_filtered_out(self, word: str) -> bool:
        return not self._filters.apply(word)

    def _get_word_from_file(self):
        self._file.seek(0)
        for _ in range(random.randrange(self._file_length)):
            self._file.readline()
        return self._file.readline()
