import random
from typing import IO

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

from hangman.filters import FilterCollection


class _WordPicker(QObject):
    publish_word = pyqtSignal(str)

    # def __init__(self, word_count, path, filters=None):
    def __init__(self, word_count, file_obj: IO[str], filters=None):
        super().__init__()
        self._word_count = word_count
        # self._path = path
        self._file_obj = file_obj
        self._filters = filters

    def pick(self):
        while True:
            # word = self._get_word(
            #     at_index=self._get_index(self._word_count),
            #     from_path=self._path
            # )
            word = self._get_word(
                at_index=self._get_index(self._word_count),
                from_file=self._file_obj
            )
            if word and not self._filters:
                break
            if self._filters.apply(word):
                break

            self._file_obj.seek(0)

        # noinspection PyUnresolvedReferences
        self.publish_word.emit(word.upper())
        self._file_obj.close()

    # def _get_word(self, *, at_index: int, from_path: str) -> str:
    def _get_word(self, *, at_index: int, from_file: IO[str]) -> str:
        # with open(from_path, "r") as infile:
        word = self._find_word_in_file(at_index, from_file)
        return word

    @staticmethod
    def _get_index(upper_limit: int) -> int:
        return random.randrange(0, upper_limit)

    @staticmethod
    def _find_word_in_file(at_index: int, file: IO[str]) -> str:
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
        file = open(self._path, "r")
        # picker = _WordPicker(self._word_count, self._path, self._filters)
        picker = _WordPicker(self._word_count, file, self._filters)
        # noinspection PyUnresolvedReferences
        picker.publish_word.connect(self._receive_word)
        word_picker = _WordPickerRunnable(picker)
        QThreadPool.globalInstance().start(word_picker)

    def _receive_word(self, word: str) -> None:
        # noinspection PyUnresolvedReferences
        self.publish_word.emit(word.upper())
