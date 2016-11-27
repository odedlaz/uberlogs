from copy import copy
from logging import Formatter as LoggingFormatter
from ..private import extract_keywords


class UberFormatter(LoggingFormatter):

    def __init__(self, parse_text=False, include_format_keywords=False, **kwargs):
        super(UberFormatter, self).__init__(**kwargs)
        self.parse_text = parse_text
        self.include_format_keywords = include_format_keywords

    def uber_record(self, record):
        return getattr(record, 'uber', False)
