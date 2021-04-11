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
def word_picker():
    return WordPicker()


def test__get_word_from_file(word_picker, file_obj):
    file, _ = file_obj
    assert word_picker._get_word_from_file_at_index(file=file, index=6) == "NANTUCKET"
    file.seek(0)
    assert word_picker._get_word_from_file_at_index(file=file, index=1) == "ONCE"
    file.seek(0)
    assert word_picker._get_word_from_file_at_index(file=file, index=15) == "SUCK"
    file.seek(0)
    assert word_picker._get_word_from_file_at_index(file=file, index=10) == "DICK"


def test_word_picker(word_list, file_obj, word_picker):
    file, length = file_obj
    word = word_picker(length, file)
    assert word in word_list
