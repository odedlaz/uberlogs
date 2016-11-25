import json
import copy
from datetime import datetime
from logging import Formatter as LoggingFormatter

from ..private import (JsonEncoder,
                       rewrite_record,
                       string_formatter,
                       extract_keywords)


class JsonFormatter(LoggingFormatter):

    def __init__(self, parse_text=False,
                 include_format_keywords=True,
                 indent=None,
                 fmt=None,
                 datefmt=None, **kwargs):
        """
        Initialize the handler.
        If stream is not specified, sys.stderr is used.
        """
        if not all(x is None for x in [fmt, datefmt]):
            msg = "JsonFormatter doesn't allow to set 'format' and 'datefmt'!"
            raise ValueError(msg)

        super(JsonFormatter, self).__init__(fmt="%(json)s", **kwargs)
        self.parse_text = parse_text
        self.include_format_keywords = include_format_keywords
        self.indent = indent

    def formatException(self, exc_info):
        """
        does nothing, because the default formatException
        dumps the formatted exception in a non json format
        """
        return ""

    def format(self, record):
        # create a clone of the record,
        # to make sure we don't change the original
        record = copy.copy(record)

        # get the message and format it
        message = record.getMessage()

        kw = list(extract_keywords(message))

        arguments = {arg.key: arg.value
                     for arg in rewrite_record(record)}

        if self.parse_text:
            message = message.format(**arguments)

        include_keywords = self.include_format_keywords
        if not self.parse_text:
            include_keywords = True

        message = dict(message=message,
                       logger=record.name,
                       level=record.levelname,
                       file=record.pathname,
                       func=record.funcName,
                       time=datetime.fromtimestamp(record.created),
                       **{k: v for k, v in arguments.items()
                          if include_keywords or k not in kw})

        if record.exc_info:
            fn = LoggingFormatter.formatException
            message["exc_info"] = fn(self, record.exc_info)

        record.json = json.dumps(message,
                                 sort_keys=True,
                                 indent=self.indent,
                                 cls=JsonEncoder)
        # call the original handler
        return super(JsonFormatter, self).format(record)
