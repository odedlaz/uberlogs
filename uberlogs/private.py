import six
import logging
import logging.config
from string import Formatter as StringFormatter
from inspect import currentframe as currentframe
from random import choice
if six.PY3:
    from _string import formatter_field_name_split
    maketrans = str.maketrans
elif six.PY2:
    from string import maketrans
    formatter_field_name_split = str._formatter_field_name_split
else:
    raise ImportError("Unknown python version")


class LRUCache(dict):

    def __init__(self, max_items=None, **kwargs):
        if max_items is not None and not isinstance(max_items, int):
            raise ValueError("max items has to be an integer")

        if max_items <= 0:
            raise ValueError("max items has to be at least 1")

        self.max_items = max_items
        super(LRUCache, self).__init__(**kwargs)

    def __setitem__(self, key, value):
        if self.max_items is not None and len(self) >= self.max_items:
            self.popitem()
        return super(LRUCache, self).__setitem__(key, value)


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


persistent_cache = {}
temporary_cache = LRUCache(max_items=100)


class UberLogRecord(object):
    __slots__ = ["text",
                 "keyword_keys",
                 "code"]

    reserved_varnames = {"level", "msg", "args", "exc_info"}

    @classmethod
    def compile(cls, text, args):
        """
        create a UberLogRecord instance of the given text and args
        """
        raw_keywords = {formatter_field_name_split(kw)[0] for _, kw, _, _
                        in string_formatter.parse(text, silent=True) if kw}

        keywords = {kw: kw.translate(valid_chars_transtable) for kw
                    in raw_keywords if kw not in args}

        arguments = {k for k in six.iterkeys(args) if k in raw_keywords}
        # create a valid log message (some characters aren't allowed)
        # and create the code that extracts keyword statements
        valid_text = text
        code = ["uber_kw = {}"]
        for kw, valid_kw in six.iteritems(keywords):
            vfn = valid_kw.replace('"', r'\"')
            code.append('uber_kw["{vfn}"] = {fn}'.format(vfn=vfn,
                                                         fn=kw))
            valid_text = valid_text.replace(kw, valid_kw)

        keyword_keys = set(six.itervalues(keywords)).union(arguments)

        # check if the varnames used for logging are reserved.
        # That can be the case if either:
        # 1. parsed keywords contain reserved varnames
        # 2. kwargs contain reserved varnames
        # 3. extra contains reserved varnames

        varnames = keyword_keys.union(args.keys())
        used_reserved_names = cls.reserved_varnames.intersection(varnames)
        if used_reserved_names:
            random_reserved_name = choice(list(used_reserved_names))
            m = "{fn}() got multiple values for keyword argument: '{reserved}'"
            raise TypeError(m.format(fn="log_message",
                                     reserved=random_reserved_name))

        return cls(text=valid_text,
                   keyword_keys=keyword_keys,
                   code=compile("\n".join(code),
                                '<string>',
                                'exec'))

    def __init__(self, text, keyword_keys, code):
        self.text = text
        self.keyword_keys = keyword_keys
        self.code = code


valid_chars_transtable = maketrans("[].", "___")


def text_keywords(text, caller, log_args):
    """
    extract keyword arguments from format text
    and evaluate them in caller scope.
    """

    # Try to get the log message from the persistent cache
    # if it's not there -> try the temporary_cache
    # 1. If it's in the temporary cache - move to persistent cache
    # 2. Otherwise, Compile the log and cache it in the temporary cache
    # The idea behind these two caches is that logs might be written once
    # and we don't want to cache them forever.
    log_msg = persistent_cache.get(text)
    if log_msg is None:
        log_msg = temporary_cache.pop(text, None)

        cache = persistent_cache
        if log_msg is None:
            cache = temporary_cache
            log_msg = UberLogRecord.compile(text, log_args)

        cache[text] = log_msg

    # execute the compiled code in caller context
    exec(log_msg.code, caller.f_globals, caller.f_locals)

    return log_msg.text, log_msg.keyword_keys, caller.f_locals.pop("uber_kw")


def log_message(logger, level, msg, args, exc_info=None, extra=None, **kwargs):
    extra = extra or {}
    if kwargs:
        extra.update(kwargs)

    frame = currentframe()

    # _log -> log_message -> profile
    caller = frame.f_back.f_back

    # why delete the frame?
    # VERSION: 2 or 3
    # https://docs.python.org/VERSION/library/inspect.html#the-interpreter-stack
    del frame
    if not isinstance(msg, six.string_types):
        raise ValueError(("message has to be a string, "
                          "got: {}({})").format(str(msg), str(type(msg))))

    msg, keyword_keys, keywords = text_keywords(text=msg,
                                                caller=caller,
                                                log_args=extra)
    if keywords:
        extra.update(keywords)
    return logging.Logger._log(logger, level, msg, args, exc_info,
                               extra=dict(uber_extra=extra,
                                          uber_kws=keyword_keys,
                                          **extra))
