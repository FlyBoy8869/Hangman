from io import StringIO

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
def word_picker(file_obj):
    file, length = file_obj
    return WordPicker(file, length)


def test_word_picker(word_list, word_picker):
    assert word_picker.pick() in word_list
