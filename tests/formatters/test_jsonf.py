from __future__ import print_function
import six
from mock import MagicMock, call, patch, mock_open
from ddt import ddt, data, unpack
from unittest import TestCase

from uberlogs.formatters import JsonFormatter


@ddt
class JsonFormatterTests(TestCase):
    pass
