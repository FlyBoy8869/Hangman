import random
from pathlib import Path


class WordSelector:
    def __init__(self, word_file: Path):
        self._path: Path = word_file
        self._word_list = self._load_word_list()

    def select(self) -> str:
        while self._has_apostrophe(word := random.choice(self._word_list)):
            # choose another
            pass

        return word.upper()

    @staticmethod
    def _has_apostrophe(word: str):
        return "'" in word

    def _load_word_list(self) -> list[str]:
        with self._path.open(mode="r", encoding="utf-8") as file:
            word_list = [word.strip() for word in file if word]

        return word_list


if __name__ == '__main__':
    ws = WordSelector(Path("words.txt"))
    print(ws.select())
