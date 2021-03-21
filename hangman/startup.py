from pathlib import Path

from hangman import config

_base_folder = "resources/data/words"
_temp_file = "working_words.dat"

_all_words = "resources/data/words/words.dat"
_all_words_length = 370103


def _make_file_genny(path):
    with open(path, "r") as infile:
        for word in infile:
            yield word


def _make_file_list(names: list[int, ...]) -> list[Path, ...]:
    return [Path(_base_folder) / (str(name) + ".dat") for name in names]


def _combine_files(paths: list[Path, ...]) -> int:
    path = Path(_base_folder) / _temp_file
    with open(path, "w") as outfile:
        total_length: int = 0
        for name in paths:
            for word in _make_file_genny(name):
                total_length += 1
                outfile.write(word)

    print(f"{total_length=}")
    return total_length


def _create_working_words_file(lengths: list[int, ...]):
    if lengths:
        paths = _make_file_list(lengths)
        file_length = _combine_files(paths)
        config.add_attribute("working_length", file_length)
        config.add_attribute("working_file", Path(_base_folder) / _temp_file)
    else:
        config.add_attribute("working_length", _all_words_length)
        config.add_attribute("working_file", Path(_all_words))


def do_startup():
    _create_working_words_file(config.config.range)
