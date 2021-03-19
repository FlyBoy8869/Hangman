import random
import sys
import time

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from hangman.config import config


class Filter:
    """Return True if filter succeeds."""
    def filter(self, word: str):
        pass


class WordPicker(QObject):
    publish_word = pyqtSignal(str)

    def __init__(self, selection_filters: list[Filter] = None):
        super().__init__()
        self._filters: list[Filter, ...] = [NoApostropheFilter(), NoNumbersFilter(), ]
        if selection_filters:
            self._filters += selection_filters

    def add_filter(self, _filter: Filter):
        assert isinstance(_filter, Filter), f"invalid type {type(_filter)}"
        self._filters.append(_filter)

    def pick_a_word(self):
        word_picker = _WordPicker(config.word_file_path, self._filters)
        # noinspection PyUnresolvedReferences
        word_picker.signals.publish_word.connect(lambda word: self.publish_word.emit(word.upper()))
        QThreadPool.globalInstance().start(word_picker)


def _word_generator(path):
    with open(path, "r") as in_file:
        for index, word in enumerate(in_file):
            yield index, word.strip()


class _WordPicker(QRunnable):
    class Signals(QObject):
        publish_word = pyqtSignal(str)

    def __init__(self, path, filters):
        super().__init__()
        self._word_list_path = path
        self._filters = filters
        self.signals = self.Signals()

    def run(self):
        attempts = 0
        word = ""
        start_time = time.time()
        while True:
            attempts += 1
            index = random.randrange(0, config.number_of_words)
            genny = _word_generator(self._word_list_path)
            ic(id(genny))
            ic(sys.getsizeof(genny))
            for word_index, word in genny:
                if word_index == index:
                    ic(index, word, len(word))
                    break

            if all(self._apply_filters_to(word)):
                ic(time.time() - start_time)
                ic(attempts)
                # noinspection PyUnresolvedReferences
                self.signals.publish_word.emit(word)
                return

    def _apply_filters_to(self, word: str):
        return [_filter.filter(word) for _filter in self._filters]


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
