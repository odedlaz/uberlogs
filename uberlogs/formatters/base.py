from logging import Formatter as LoggingFormatter


class UberFormatter(LoggingFormatter):

    def __init__(self, parse_text=False, include_format_keywords=False, **kwargs):
        super(UberFormatter, self).__init__(**kwargs)
        self.parse_text = parse_text
        self.include_format_keywords = include_format_keywords

    def uber_record(self, record):
        return hasattr(record, 'uber_extra') \
            and hasattr(record, 'uber_kws')
