from __future__ import print_function
import os
import sys
import time
import logging
import uberlogs
from six.moves import range
from collections import namedtuple

Person = namedtuple('Person', ['name', 'age'])


class TimeIt(object):

    def __init__(self, scope_name="", fd=sys.stdout):
        self._start = None
        self._fd = fd
        self._fmt = 'took {{secs:.5f}} seconds to run [{}]'.format(scope_name)

    def __enter__(self):
        self._start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        now = time.time() - self._start
        print(self._fmt.format(secs=now).strip(), file=self._fd)


uberlogs.install()
uber_logger = uberlogs.getLogger("uber")
std_logger = logging.getLogger("std")
p = Person(name="oded", age=26)

iterations = int(os.getenv("ITERATIONS", 1))

msg = "Profiling {} iterations".format(iterations)
print("{msg}\n{underline}".format(msg=msg,
                                  underline="-" * len(msg)),
      file=sys.stderr)

# run test with std logging using % formatting
old_simple_fmt = "Hey! my name is %s, and my age is: %s!"
with TimeIt(scope_name="std %", fd=sys.stderr):
    for _ in range(iterations):
        std_logger.info(old_simple_fmt, p.name, p.age)

# run test with std logging using .format() formatting
simple_fmt = "Hey! my name is {p_name}, and my age is: {p_age}!"
with TimeIt(scope_name="std .format()", fd=sys.stderr):
    for _ in range(iterations):
        std_logger.info(simple_fmt.format(p_name=p.name, p_age=p.age))

# run test with uberlog using .format() formatting
with TimeIt(scope_name="uber .format()", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(simple_fmt, p_name=p.name, p_age=p.age)

# run test with uberlog using .format() formatting, with statement evaluation
statement_fmt = "Hey! my name is {p.name}, and my age is: {p.age}!"
with TimeIt(scope_name="uber .format() with statement", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(statement_fmt)
