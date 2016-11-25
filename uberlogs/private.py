import json
import logging
import logging.config
from collections import namedtuple
from string import Formatter as StringFormatter
from datetime import datetime, tzinfo, timedelta
from inspect import currentframe as currentframe


FIELD_PREFIX = "__"

KeyValueTuple = namedtuple('KeyValueTuple', ['key', 'value'])


class JsonEncoder(json.JSONEncoder):

    class SimpleUTC(tzinfo):

        def tzname(self):
            return "UTC"

        def utcoffset(self, dt):
            return timedelta(0)

    def default(self, obj):
        if isinstance(obj, datetime):
            dt = obj.replace(tzinfo=JsonEncoder.SimpleUTC(),
                             microsecond=0)
            return dt.isoformat()
        return json.JSONEncoder.default(self, obj)


class UberStringFormatter(StringFormatter):

    def parse(self, text, silent=False):
        try:
            for field in StringFormatter.parse(self, text):
                yield field
        except ValueError:
            # If string can't be formatted
            # We silence the error and return nothing
            if not silent:
                raise

string_formatter = UberStringFormatter()


def extract_keywords(text, silent=False):
    for _, fname, _, _ in string_formatter.parse(text, silent=silent):
        if fname:
            yield fname


def text_keywords(text, caller, **log_args):
    """
    extract keyword arguments from format text
    and evaluate them in caller scope.
    """
    keywords = {}
    for fname in extract_keywords(text, silent=True):
        if fname in log_args:
            continue

        # valid format names can't have dots in them
        valid_fname = fname.replace(".", "_")
        keywords[valid_fname] = eval(fname,
                                     caller.f_globals,
                                     caller.f_locals)

        # update the format text to have valid names
        text = text.replace(fname, valid_fname)

    return text, keywords


def rewrite_record(record):
    """
    rewrite the record to remove unique fields __ prefix.
    :return: the unique fields
    """
    for key, value in record.__dict__.items():
        if not key.startswith(FIELD_PREFIX):
            continue
        skey = key.lstrip(FIELD_PREFIX)
        delattr(record, key)
        if hasattr(record, skey):
            fmt = "'{key}' string is reserved for logging ({msg})"
            raise ValueError(fmt.format(key=skey, msg=record.msg))
        setattr(record, skey, value)
        yield KeyValueTuple(key=skey,
                            value=value)


def log_message(logger, level, msg, args, exc_info=None, extra=None, **kwargs):
    unified_args = dict(extra, **kwargs) if extra else kwargs

    frame = currentframe()

    msg, keywords = text_keywords(text=msg,
                                  caller=frame.f_back.f_back,
                                  **unified_args)

    unified_args.update(keywords)

    extra = {FIELD_PREFIX + key: val for key, val in unified_args.items()}
    try:
        return logging.Logger._log(logger, level, msg, args, exc_info, extra)
    finally:
        # why delete the frame?
        # VERSION: 2 or 3
        # https://docs.python.org/VERSION/library/inspect.html#the-interpreter-stack
        del frame
