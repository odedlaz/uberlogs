import logging
import logging.config
from .private import (text_keywords,
                      FIELD_PREFIX,
                      log_message)
from functools import partial


try:
    from twisted.logger import (globalLogPublisher,
                                STDLibLogObserver)
    rewire_twisted_log = True
except ImportError:
    rewire_twisted_log = False


def getLogger(name):
    if not isinstance(name, str):
        name = name.__class__.__name__

    logger = logging.getLogger(name)
    logger._log = partial(log_message, logger)
    return logger


def install(default_path='logging.json',
            default_level=logging.INFO,
            env_key='LOG_CFG',
            kill_on=None):
    """
    Setup logging configuration
    if the path in the default_path or env_key doesn't exist,
    default level is used, and the root handler is set to the formattable stream handler
    """
    from .handlers import KillProcessHandler
    from . import level
    import os
    import sys

    path = os.getenv(env_key, default_path)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            import json
            content = json.load(f)
        logging.config.dictConfig(content)
    else:
        from .formatters import ConcatFormatter

        logging.root.addHandler(StreamHandler(sys.stdout))
        logging.root.setFormatter(ConcatFormatter())
        logging.root.level = default_level
        basicConfig(level=default_level)

    # this handler is the last one, and will force exit
    # once a cirtical message has been recieved
    if kill_on is not None:
        logging.root.addHandler(KillProcessHandler(level=kill_on))

    def log_unhandled(exctype, value, tb):
        getLogger("unhandled").critical("Unhandled Error",
                                        exc_info=(exctype, value, tb))

    sys.excepthook = log_unhandled

    if rewire_twisted_log:
        # clear all observers
        map(globalLogPublisher.removeObserver,
            globalLogPublisher._observers)

        globalLogPublisher.addObserver(STDLibLogObserver())
