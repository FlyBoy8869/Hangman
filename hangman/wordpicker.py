import random
import time

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

from hangman.config import config
from hangman.filters import Filter, NoApostropheFilter, NoNumbersFilter


def _word_generator(path):
    with open(path, "r") as in_file:
        for index, word in enumerate(in_file):
            yield index, word.strip()


class WordPicker(QObject):
    publish_word = pyqtSignal(str)

    def __init__(self, selection_filters: list[Filter] = None):
        super().__init__()
        self._have_word = False
        self._filters: list[Filter, ...] = [NoApostropheFilter(), NoNumbersFilter(), ]
        if selection_filters:
            self._filters += selection_filters

    def add_filter(self, _filter: Filter):
        assert isinstance(_filter, Filter), f"invalid type {type(_filter)}"
        self._filters.append(_filter)

    def pick_a_word(self):
        picker = _Picker(config.working_length, config.working_file, self._filters)
        # noinspection PyUnresolvedReferences
        picker.publish_word.connect(self._receive_word)
        word_picker = _WordPicker(picker)
        QThreadPool.globalInstance().start(word_picker)

    def _receive_word(self, word: str) -> None:
        # noinspection PyUnresolvedReferences
        self.publish_word.emit(word.upper())


class _Picker(QObject):
    publish_word = pyqtSignal(str)

    def __init__(self, file_length, path, filters=None):
        super().__init__()
        self._file_length = file_length
        self._path = path
        self._filters = filters

    def pick(self):
        word = ""
        start_time = time.time()
        while True:
            index = random.randrange(0, self._file_length)
            ic(index)
            genny = _word_generator(self._path)
            for word_index, word in genny:
                if word_index == index:
                    break

            if all(self._apply_filters_to(word)):
                ic(time.time() - start_time)
                ic(word)
                # noinspection PyUnresolvedReferences
                self.publish_word.emit(word.upper())
                return

    def _apply_filters_to(self, _word: str):
        return [_filter.filter(_word) for _filter in self._filters]


class _WordPicker(QRunnable):
    def __init__(self, picker):
        super().__init__()
        self._picker = picker

    def run(self) -> None:
        self._picker.pick()
