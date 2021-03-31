from io import StringIO

# noinspection PyPackageRequirements
import pytest

from hangman.wordpicker import _WordPickerWorker


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
    return _WordPickerWorker(length, file)


def test__get_index(word_picker_worker):
    upper_limit = 6
    for _ in range(1_000_000):
        assert 0 <= word_picker_worker._get_index(upper_limit) < upper_limit


def test__get_word_from_file(word_picker_worker, file_obj):
    file, _ = file_obj
    assert word_picker_worker._get_word_from_file(6, file) == "NANTUCKET"
    file.seek(0)
    assert word_picker_worker._get_word_from_file(1, file) == "ONCE"
    file.seek(0)
    assert word_picker_worker._get_word_from_file(15, file) == "SUCK"
    file.seek(0)
    assert word_picker_worker._get_word_from_file(10, file) == "DICK"


def test_pick(word_picker_worker, word_list, file_obj, capsys):
    file, _ = file_obj
    word_picker_worker.publish_word.connect(lambda word: print(word))
    word_picker_worker.pick()
    captured = capsys.readouterr()
    assert captured.out.strip() in word_list
    assert file.closed
