import json
import copy
from logging import Formatter as LoggingFormatter
from datetime import datetime, tzinfo, timedelta

from .. import level
from ..private import (rewrite_record,
                       string_formatter,
                       extract_keywords)


class ConcatFormatter(LoggingFormatter):
    message_format = u"{0.key}{1}{0.value}"
    log_line_format = u"{message}{delimiter}{parameters}"

    def __init__(self, operator=":",
                 delimiter=";",
                 log_in_color=False,
                 parse_text=False,
                 include_format_keywords=False,
                 **kwargs):
        """
        Initialize the handler.
        """
        super(ConcatFormatter, self).__init__(**kwargs)
        # https://docs.python.org/2/library/logging.html#logrecord-attributes
        self.delimiter = delimiter
        self.operator = operator
        self.parse_text = parse_text
        self.color = log_in_color
        self.include_format_keywords = include_format_keywords
        if self.color:
            globals()["colorclass"] = __import__("colorclass")
            self._color_fmt = '{{{color}}}{text}{{/{color}}}'
            self._log_message_color = {
                level.DEBUG: "cyan",
                level.INFO: "white",
                level.WARNING: "yellow",
                level.ERROR: "red",
                level.CRITICAL: "magenta",
            }

    def format(self, record):
        # create a clone of the record,
        # to make sure we don't change the original
        record = copy.copy(record)

        # couldn've used list(...) but less understandable
        arguments = [arg for arg in rewrite_record(record)]
        # get the none formatted message (not getMessage())
        message = str(record.msg)

        kw = list(extract_keywords(message))

        if self.parse_text:

            message = message.format(**{f.key: f.value
                                        for f in arguments})

        if arguments:
            include_keywords = self.include_format_keywords
            if not self.parse_text:
                include_keywords = True

            parameters = [self.message_format.format(arg, self.operator)
                          for arg in arguments if include_keywords or arg.key not in kw]

            if parameters:
                message = self.log_line_format.format(message=message,
                                                      delimiter=self.delimiter,
                                                      parameters=self.delimiter.join(sorted(parameters)))

        if self.color:
            color = self._log_message_color[record.levelno]
            message = colorclass.Color(self._color_fmt.format(text=message,
                                                              color=color))

        record.msg = message

        # call the original handler
        return super(ConcatFormatter, self).format(record)
