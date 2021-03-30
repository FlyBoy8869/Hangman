from io import StringIO
from unittest import TestCase

from hangman.wordpicker import _WordPicker


class Test_WordPicker(TestCase):
    def setUp(self) -> None:
        sentence = "There once was a man from nantucket who had a dick so long he could suck it".upper()
        word_list = sentence.split(" ")
        self.words = "\n".join(word_list)
        self.buffer = StringIO(self.words)

        self.wp = _WordPicker(len(word_list), self.buffer)

        self.received_word = ""

    def tearDown(self) -> None:
        self.buffer.close()

    def test_pick_no_filters(self):
        def word_published(word):
            self.received_word = word

        self.wp.publish_word.connect(word_published)
        self.wp.pick()
        self.assertIn(self.received_word, self.words)

    def test__get_word(self):
        word = self.wp._get_word(at_index=6, from_file=self.wp._file_obj)
        self.assertEqual("NANTUCKET", word, f"{word} != expected NANTUCKET")

    def test__get_index(self):
        # not sure about the validity of this test
        # i.e., is the testing method even sound, is 1 million tests statistically enough
        upper_limit = 6
        for _ in range(1_000_000):
            index = self.wp._get_index(upper_limit)
            self.assertGreaterEqual(index, 0)
            self.assertLess(index, upper_limit)

    def test__find_word_in_file(self):
        index = 6
        assert self.wp._find_word_in_file(index, self.buffer) == "NANTUCKET", "Whoops"
