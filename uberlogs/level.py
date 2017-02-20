from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL, FATAL, NOTSET


NAME_TO_VALUE = {"DEBUG": DEBUG,
                 "INFO": INFO,
                 "WARN": WARN,
                 "WARNING": WARNING,
                 "ERROR": ERROR,
                 "CRITICAL": CRITICAL,
                 "FATAL": FATAL,
                 "NOTSET": NOTSET
                 }

VALUE_TO_NAME = {v: k for k, v in NAME_TO_VALUE.items()}

ALL = VALUE_TO_NAME.keys()
