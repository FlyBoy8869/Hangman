import random
from typing import IO

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

from hangman.filters import FilterCollection


class _WordPicker(QObject):
    publish_word = pyqtSignal(str)

    def __init__(self, word_count, file_obj: IO[str], filters=None):
        super().__init__()
        self._word_count = word_count
        self._file_obj = file_obj
        self._filters = filters

    def pick(self):
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

        # noinspection PyUnresolvedReferences
        self.publish_word.emit(word.upper())
        self._file_obj.close()

    @staticmethod
    def _get_index(upper_limit: int) -> int:
        return random.randrange(0, upper_limit)

    @staticmethod
    def _get_word_from_file(at_index: int, file: IO[str]) -> str:
        for index, word in enumerate(file):
            if at_index == index:
                return word.strip()


class _WordPickerRunnable(QRunnable):
    def __init__(self, picker):
        super().__init__()
        self._picker = picker

    def run(self) -> None:
        self._picker.pick()


class WordPicker(QObject):
    publish_word = pyqtSignal(str)

    def __init__(self, word_count: int, path: str, selection_filters: FilterCollection = None):
        super().__init__()
        self._word_count = word_count
        self._path = path
        self._filters = selection_filters

    def set_filters(self, filters: FilterCollection):
        self._filters = filters

    def pick_a_word(self):
        picker = _WordPicker(self._word_count, open(self._path), self._filters)
        # noinspection PyUnresolvedReferences
        picker.publish_word.connect(self._receive_word)
        word_picker = _WordPickerRunnable(picker)
        QThreadPool.globalInstance().start(word_picker)

    def _receive_word(self, word: str) -> None:
        # noinspection PyUnresolvedReferences
        self.publish_word.emit(word.upper())
