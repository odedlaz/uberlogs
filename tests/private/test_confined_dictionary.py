from __future__ import print_function
import six
from ddt import ddt, data
from unittest import TestCase

from uberlogs.private import ConfinedDictionary


@ddt
class ConfinedDictionaryTests(TestCase):

    def test_value_error_raise_on_non_integer_max_items(self):
        with self.assertRaises(ValueError):
            ConfinedDictionary("a-non-int-value")

    @data(0, -1)
    def test_value_error_raise_on_non_positive_max_items(self, max_items):
        with self.assertRaises(ValueError):
            ConfinedDictionary(max_items)

    def test_resize_on_max_items(self):
        cd = ConfinedDictionary(max_items=1, test_key="test")
        self.assertEqual(len(cd), 1)

        cd["another_test_key"] = "another_test"
        self.assertEqual(len(cd), 1)
        self.assertIn("another_test_key", cd)
        self.assertNotIn("test_key", cd)

    def test_no_resize_when_max_items_not_reached(self):
        cd = ConfinedDictionary(max_items=2)
        cd["a"] = "test-a"
        self.assertEqual(len(cd), 1)

        cd["b"] = "test-b"
        self.assertEqual(len(cd), 2)
        six.assertCountEqual(self, cd.keys(), ["a", "b"])

        cd["c"] = "test-c"
        self.assertEqual(len(cd), 2)
        self.assertIn("c", cd)
