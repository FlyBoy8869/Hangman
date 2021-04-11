from io import StringIO

# noinspection PyPackageRequirements
import pytest

from hangman.wordpicker import WordPicker


@pytest.fixture
def word_list():
    sentence = "there once was a man from nantucket who had a dick so long he could suck it".upper()
    #          "  0     1   2  3  4   5       6      7   8  9  10  11  12  13   14   15  16"
    return sentence.split(" ")


@pytest.fixture
def file_obj(word_list):
    buffer = StringIO("\n".join(word_list))
    yield buffer, len(word_list)
    buffer.close()


@pytest.fixture
def word_picker_worker(word_list, file_obj):
    file, length = file_obj
    return WordPicker(length, file)


def test__get_index(word_picker_worker):
    upper_limit = 6
    for _ in range(1_000_000):
        assert 0 <= word_picker_worker._get_index(upper_limit) < upper_limit


def test__get_word_from_file(word_picker_worker, file_obj):
    file, _ = file_obj
    assert word_picker_worker._get_word_from_file_at_index(file=, index=) == "NANTUCKET"
    file.seek(0)
    assert word_picker_worker._get_word_from_file_at_index(file=, index=) == "ONCE"
    file.seek(0)
    assert word_picker_worker._get_word_from_file_at_index(file=, index=) == "SUCK"
    file.seek(0)
    assert word_picker_worker._get_word_from_file_at_index(file=, index=) == "DICK"


def test_pick(word_picker_worker, word_list, file_obj):
    file, _ = file_obj
    word = word_picker_worker.pick_a_word()
    assert word.strip() in word_list
    assert file.closed
