import random

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

from hangman.filters import FilterCollection


class _WordPicker(QObject):
    publish_word = pyqtSignal(str)

    def __init__(self, word_count, path, filters=None):
        super().__init__()
        self._word_count = word_count
        self._path = path
        self._filters = filters

    def pick(self):
        while True:
            genny = self._word_generator(self._path)
            index = random.randrange(0, self._word_count)
            word = ""
            for word_index, word in genny:
                if word_index == index:
                    break

            if self._filters.apply(word):
                # noinspection PyUnresolvedReferences
                self.publish_word.emit(word.upper())
                return

    @staticmethod
    def _word_generator(path):
        with open(path, "r") as in_file:
            for index, word in enumerate(in_file):
                yield index, word.strip()


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
        picker = _WordPicker(self._word_count, self._path, self._filters)
        # noinspection PyUnresolvedReferences
        picker.publish_word.connect(self._receive_word)
        word_picker = _WordPickerRunnable(picker)
        QThreadPool.globalInstance().start(word_picker)

    def _receive_word(self, word: str) -> None:
        # noinspection PyUnresolvedReferences
        self.publish_word.emit(word.upper())
