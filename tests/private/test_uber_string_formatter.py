import six
from unittest import TestCase

from uberlogs.private import UberStringFormatter


class UberStringFormatterTests(TestCase):

    def setUp(self):
        self.formatter = UberStringFormatter()
        self.invalid_format = "{[blabla]"

    def test_raise_on_invalid_format_when_not_silent(self):
        with self.assertRaises(Exception):
            list(self.formatter.parse(self.invalid_format, silent=False))

    def test_no_raise_on_invalid_format_when_silent(self):
        list(self.formatter.parse(self.invalid_format, silent=True))
