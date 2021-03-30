# noinspection PyPackageRequirements
import pytest

from io import StringIO

from hangman.wordpicker import _WordPicker


class Fixture:
    def __init__(self):
        sentence = "there once was a man from nantucket who had a dick so long he could suck it".upper()
        #          "  0     1   2  3  4   5       6      7   8  9  10  11  12  13   14   15  16"
        self.word_list = sentence.split(" ")
        self.file_obj = StringIO("\n".join(self.word_list))
        self.wp_protected = _WordPicker(len(self.word_list), self.file_obj)
        self.wp_protected.publish_word.connect(lambda word: print(word))


@pytest.fixture
def fixture():
    return Fixture()


def test__get_index(fixture):
    upper_limit = 6
    for _ in range(1_000_000):
        assert 0 <= fixture.wp_protected._get_index(upper_limit) < upper_limit


def test__get_word_from_file(fixture):
    assert fixture.wp_protected._get_word_from_file(6, fixture.file_obj) == "NANTUCKET"
    fixture.file_obj.seek(0)
    assert fixture.wp_protected._get_word_from_file(1, fixture.file_obj) == "ONCE"
    fixture.file_obj.seek(0)
    assert fixture.wp_protected._get_word_from_file(15, fixture.file_obj) == "SUCK"
    fixture.file_obj.seek(0)
    assert fixture.wp_protected._get_word_from_file(10, fixture.file_obj) == "DICK"


def test_pick(fixture, capsys):
    fixture.wp_protected.pick()
    captured = capsys.readouterr()
    assert captured.out.strip() in fixture.word_list
    assert fixture.file_obj.closed
