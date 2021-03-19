import random
import time
from pathlib import Path

from PyQt5.QtCore import QRunnable, pyqtSignal, QThreadPool, QObject


class Filter:
    """Return True if filter succeeds."""
    def filter(self, word: str):
        pass


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


class WordList(QObject):
    publish_word = pyqtSignal(str)

    @classmethod
    def create_from_file(cls, file: Path):
        with file.open(mode="r", encoding="utf-8") as file:
            word_list = [word.strip() for word in file if word]
        return cls(word_list)

    def __init__(self, word_list: list[str], selection_filters: list[Filter] = None):
        super().__init__()
        self._word_list = word_list
        self._filters: list[Filter, ...] = [NoApostropheFilter(), NoNumbersFilter(), ]
        if selection_filters:
            self._filters += selection_filters

    def add_filter(self, _filter: Filter):
        assert isinstance(_filter, Filter), f"invalid type {type(_filter)}"
        self._filters.append(_filter)

    def pick_a_word(self):
        word_picker = _WordPicker(self._word_list, self._filters)
        # noinspection PyUnresolvedReferences
        word_picker.signals.publish_word.connect(lambda word: self.publish_word.emit(word.upper()))
        QThreadPool.globalInstance().start(word_picker)


class _WordPicker(QRunnable):
    class Signals(QObject):
        publish_word = pyqtSignal(str)

    def __init__(self, word_list, filters):
        super().__init__()
        self._word_list = word_list
        self._filters = filters
        self.signals = self.Signals()

    def run(self):
        while word := random.choice(self._word_list):
            if all(self._apply_filters_to(word)):
                time.sleep(1.0)
                # noinspection PyUnresolvedReferences
                self.signals.publish_word.emit(word)
                return

    def _apply_filters_to(self, word: str):
        return [_filter.filter(word) for _filter in self._filters]
