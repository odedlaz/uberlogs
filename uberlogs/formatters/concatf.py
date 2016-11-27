import six
import ujson as json
import copy
from logging import Formatter as LoggingFormatter
from datetime import datetime, tzinfo, timedelta

from .. import level
from .base import UberFormatter


class ConcatFormatter(UberFormatter):
    message_format = u"{0}{operator}{1}"
    line_format = u"{message}{delimiter}{parameters}"
    color_format = "{color}{text}\x1b[0m"
    log_color_map = {
        level.DEBUG: '\x1b[32m',
        level.INFO: '\x1b[0m',
        level.WARNING: '\x1b[33m',
        level.ERROR: '\x1b[31m',
        level.CRITICAL: '\x1b[35m',
    }

    def __init__(self, operator=":",
                 delimiter=";",
                 log_in_color=False,
                 **kwargs):
        """
        Initialize the handler.
        """
        super(ConcatFormatter, self).__init__(**kwargs)
        # https://docs.python.org/2/library/logging.html#logrecord-attributes
        self.delimiter = delimiter
        self.operator = operator
        self.color = log_in_color

    @profile
    def _uber_format(self, record):
        record = copy.copy(record)

        arguments = getattr(record, "uber_extra")

        # get the none formatted message (not getMessage())
        message = str(record.msg)
        if self.parse_text:
            message = message.format(**arguments)

        if arguments:
            include_keywords = self.include_format_keywords
            if not self.parse_text:
                include_keywords = True

            kws = getattr(record, "uber_kws")

            parameters = {self.message_format.format(operator=self.operator,
                                                     *(key, val))
                          for key, val in six.iteritems(arguments)
                          if include_keywords or key not in kws}

            if parameters:
                paramstring = self.delimiter.join(sorted(parameters))
                message = self.line_format.format(message=message,
                                                  delimiter=self.delimiter,
                                                  parameters=paramstring)

        if self.color:
            color = self.log_color_map[record.levelno]
            message = self.color_format.format(color=color, text=message)

        record.msg = message

        return record

    def format(self, record):
        # create a clone of the record,
        # to make sure we don't change the original
        if self.uber_record(record):
            record = self._uber_format(record)
        # call the original handler
        return super(ConcatFormatter, self).format(record)
