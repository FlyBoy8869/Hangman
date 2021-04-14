import time
from typing import List


class Filter:
    """Return True if filter succeeds."""
    def filter(self, word: str):
        pass


class DummyFilter(Filter):
    def filter(self, word: str):
        return True


class NoApostropheFilter(Filter):
    def filter(self, word: str):
        """Return True if there are no apostrophes in word."""
        return "'" not in word


class NoNumbersFilter(Filter):
    def filter(self, word: str):
        return word.isalpha()


class BeginsWithLetterFilter(Filter):
    def __init__(self, letter: str):
        self._letter = letter.lower()

    def filter(self, word: str):
        return word.lower().startswith(self._letter)


class LengthFilter(Filter):
    """Return True if word is a certain length."""
    def __init__(self, length=None):
        self._length = length

    def filter(self, word: str) -> bool:
        return len(word) == self._length


class RangeFilter(Filter):
    def __init__(self, lengths: list[int, ...]):
        self.lengths = lengths

    def filter(self, word: str) -> bool:
        return len(word) in self.lengths


class FilterCollection:
    def __init__(self, filters: List[Filter] = None):
        self._filters = filters or list()

    def add(self, filter_: Filter):
        self._filters.append(filter_)

    def apply(self, word: str) -> bool:
        start_time = time.time()
        if all(self._apply_filters_to(word)):
            ic(time.time() - start_time)
            ic(word)
            return True
        return False

    def _apply_filters_to(self, word: str):
        return [_filter.filter(word) for _filter in self._filters]


dummy_filter_collection = FilterCollection([DummyFilter()])
