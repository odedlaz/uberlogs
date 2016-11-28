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
from collections import namedtuple


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

        self.cache[key] = value

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

compiled_log_msg_cache = LRUCache(capacity=15000)
CompiledLogMessage = namedtuple(
    'CompiledLogMessage', ['text', 'keywords', 'code'])
valid_chars_transtable = str.maketrans("[].", "___")


@profile
def text_keywords(text, caller, log_args):
    """
    extract keyword arguments from format text
    and evaluate them in caller scope.
    """
    log_msg = compiled_log_msg_cache.get(text)

    # we need to compile the message and add it to the cache
    if log_msg is None:
        keywords = [(kw, kw.translate(valid_chars_transtable)) for _, kw, _, _
                    in string_formatter.parse(text, silent=True)
                    if kw and kw not in log_args]

        # create a valid log message (some characters aren't allowed)
        # and create the code that extracts keyword statements
        valid_text = text
        code = ["uber_kw = {}"]
        for kw, valid_kw in keywords:
            code.append('uber_kw["{vfn}"] = {fn}'.format(vfn=valid_kw,
                                                         fn=kw))
            valid_text = valid_text.replace(kw, valid_kw)

        log_msg = CompiledLogMessage(text=valid_text,
                                     keywords=keywords,
                                     code=compile("\n".join(code),
                                                  '<string>',
                                                  'exec'))
        # cache it for later
        compiled_log_msg_cache[text] = log_msg

    # execute the compiled code in caller context
    exec(log_msg.code, caller.f_globals, caller.f_locals)
    return log_msg.text, caller.f_locals.pop("uber_kw")


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
                                              uber_kws=set(keywords),
                                              **extra))
    finally:
        # why delete the frame?
        # VERSION: 2 or 3
        # https://docs.python.org/VERSION/library/inspect.html#the-interpreter-stack
        del frame
