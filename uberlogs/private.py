import six
import ujson as json
import logging
import logging.config
from collections import namedtuple
from string import Formatter as StringFormatter
from datetime import datetime, tzinfo, timedelta
from inspect import currentframe as currentframe
from itertools import chain
from six.moves import builtins


class LRUCache(object):

    def __init__(self, capacity):
        from collections import OrderedDict
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        value = self.cache.get(key)
        if value is not None:
            # update the order
            self.cache[key] = value
        return value

    def __getitem__(self, key):
        return self.get(key)

    def set(self, key, value):

        if key not in self.cache:
            # before adding a new item, we update the lru cahce
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)

        self.cache[str(key)] = value

    def __setitem__(self, key, value):
        return self.set(key, value)


class UberStringFormatter(StringFormatter):

    @profile
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

memoize = LRUCache(capacity=15000)

transtable = str.maketrans("[].", "___")


@profile
def text_keywords(text, caller, log_args):
    """
    extract keyword arguments from format text
    and evaluate them in caller scope.
    """
    keywords = {}
    fnames = memoize.get(text)

    if fnames is None:
        fnames = [(fname, fname.translate(transtable)) for _, fname, _, _
                  in string_formatter.parse(text, silent=True)
                  if fname]

        memoize[text] = fnames

    for fname, valid_fname in fnames:
        # valid format names can't have dots in them

        if valid_fname in log_args:
            continue

        keywords[valid_fname] = eval(fname,
                                     caller.f_globals,
                                     caller.f_locals)

        # update the format text to have valid names
        text = text.replace(fname, valid_fname)

    return text, keywords


@profile
def log_message(logger, level, msg, args, exc_info=None, extra=None, **kwargs):
    extra = dict(extra, **kwargs) if extra else kwargs

    frame = currentframe()

    # _log -> log_message -> profile
    caller = frame.f_back.f_back.f_back

    msg, keywords = text_keywords(text=msg,
                                  caller=caller,
                                  log_args=extra)

    extra = dict(keywords, **extra)

    try:
        return logging.Logger._log(logger, level, msg, args, exc_info,
                                   extra=dict(uber_extra=extra,
                                              uber_kws=list(keywords),
                                              **extra))
    finally:
        # why delete the frame?
        # VERSION: 2 or 3
        # https://docs.python.org/VERSION/library/inspect.html#the-interpreter-stack
        del frame
