import six
from inspect import currentframe as currentframe

from .. import level
from .base import UberFormatter


class ConcatFormatter(UberFormatter):
    msg_fmt = u"{0}{operator}{1}"
    line_fmt = u"{message}{delimiter}{parameters}"
    color_fmt = "{color}{text}\x1b[0m"
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

    def _uber_message(self, record):
        # get the none formatted message (not getMessage())
        # might be a class that represents a string,
        # for example: StringifiableFromEvent in twisted
        message = record.msg \
            if isinstance(record.msg, six.string_types) \
            else six.text_type(record.msg)
        if record.uber_extra:
            if self.parse_text:
                message = message.format(**record.uber_extra)

            params = [self.msg_fmt.format(operator=self.operator, *(key, val))
                      for key, val in six.iteritems(record.uber_extra)
                      if self.include_keywords or key not in record.uber_kws]

            if params:
                paramstring = self.delimiter.join(params)
                message = self.line_fmt.format(message=message,
                                               delimiter=self.delimiter,
                                               parameters=paramstring)
        return message

    def colorize(self, text, log_level):
        color = self.log_color_map[log_level]
        return self.color_fmt.format(color=color, text=text)

    def formatException(self, exc_info):
        exc_text = super(ConcatFormatter, self).formatException(exc_info)
        if self.color:
            frame = currentframe()
            levelno = frame.f_back.f_locals["record"].levelno
            # why delete the frame?
            # VERSION: 2 or 3
            # https://docs.python.org/VERSION/library/inspect.html#the-interpreter-stack
            del frame
            exc_text = self.colorize(text=exc_text, log_level=levelno)
        return exc_text

    def format(self, record):
        message = self._uber_message(record) \
            if self.uber_record(record) \
            else record.getMessage()

        if self.color:
            message = self.colorize(text=message, log_level=record.levelno)

        record.uber_message = message

        return super(ConcatFormatter, self).format(record)
