import six
import ujson as json
import logging
import logging.config
from collections import namedtuple
from string import Formatter as StringFormatter
from datetime import datetime, tzinfo, timedelta
from inspect import currentframe as currentframe
from itertools import chain


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


def extract_keywords(record):
    extra = getattr(record, "extra", None)
    if extra is None:
        raise ValueError("extra is missing")

    return extra["kw"]


def text_keywords(text, caller, **log_args):
    """
    extract keyword arguments from format text
    and evaluate them in caller scope.
    """
    keywords = {}

    for _, fname, _, _ in string_formatter.parse(text,
                                                 silent=True):
        if not fname or fname in log_args:
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
    extra = getattr(record, "extra", None)
    if extra is None:
        raise StopIteration()

    delattr(record, "extra")

    for key, value in chain(*map(six.iteritems, [extra["extra"],
                                                 extra["kw"]])):
        if hasattr(record, key):
            fmt = "'{key}' string is reserved for logging ({msg})"
            raise ValueError(fmt.format(key=key, msg=record.msg))

        setattr(record, key, value)
        yield (key, value)


def log_message(logger, level, msg, args, exc_info=None, extra=None, **kwargs):
    extra = dict(extra, **kwargs) if extra else kwargs

    frame = currentframe()

    msg, keywords = text_keywords(text=msg,
                                  caller=frame.f_back.f_back,
                                  **extra)

    try:
        return logging.Logger._log(logger, level, msg, args, exc_info,
                                   extra=dict(extra=dict(extra=extra,
                                                         kw=keywords)))
    finally:
        # why delete the frame?
        # VERSION: 2 or 3
        # https://docs.python.org/VERSION/library/inspect.html#the-interpreter-stack
        del frame
