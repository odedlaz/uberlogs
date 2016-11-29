import six
import ujson as json
import logging
import logging.config
from string import Formatter as StringFormatter
from datetime import datetime, tzinfo, timedelta
from inspect import currentframe as currentframe
from itertools import chain
from six.moves import builtins

if six.PY3:
    from _string import formatter_field_name_split
    maketrans = str.maketrans
elif six.PY2:
    from string import maketrans
    formatter_field_name_split = str._formatter_field_name_split
else:
    raise ImportError("Unknown python version")


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

compiled_log_msg_cache = LRUCache(capacity=100)


class CompiledLogMessage(object):
    __slots__ = ["text", "keywords", "code", "cached"]

    def __init__(self, text, keywords, code):
        self.text = text
        self.keywords = keywords
        self.code = code
        self.cached = False

valid_chars_transtable = maketrans("[].", "___")


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
                    if kw and formatter_field_name_split(kw)[0] not in log_args]

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
        compiled_log_msg_cache[text] = log_msg
    elif not log_msg.cached:
        log_msg.cached = True
        compiled_log_msg_cache.capacity += 1

    # execute the compiled code in caller context
    exec(log_msg.code, caller.f_globals, caller.f_locals)
    return log_msg.text, caller.f_locals.pop("uber_kw")


@profile
def log_message(logger, level, msg, args, exc_info=None, extra=None, **kwargs):
    if extra:
        kwargs.update(extra)

    frame = currentframe()

    # _log -> log_message -> profile
    caller = frame.f_back.f_back.f_back

    # why delete the frame?
    # VERSION: 2 or 3
    # https://docs.python.org/VERSION/library/inspect.html#the-interpreter-stack
    del frame

    msg, keywords = text_keywords(text=msg,
                                  caller=caller,
                                  log_args=kwargs)
    if keywords:
        kwargs.update(keywords)

    uber_kws = set(keywords).union(kwargs)
    return logging.Logger._log(logger, level, msg, args, exc_info,
                               extra=dict(uber_extra=kwargs,
                                          uber_kws=uber_kws,
                                          **kwargs))
