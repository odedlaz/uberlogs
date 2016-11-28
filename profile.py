from __future__ import print_function
import os
import gc
import sys
import time
import logging
import uberlogs
from six.moves import range
from collections import namedtuple
Person = namedtuple('Person', ['name', 'age', 'favorite_colors', 'single'])


class TimeIt(object):

    def __init__(self, scope_name="", fd=sys.stdout):
        self._start = None
        self._fd = fd
        self._fmt = 'block took {{secs:.5f}} seconds to run [{}]'.format(
            scope_name)

    def __enter__(self):
        # run the garbage collector
        # then disable it so it won't tamper with the measurments
        gc.collect()
        gc.disable()
        self._start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        now = time.time() - self._start
        print(self._fmt.format(secs=now).strip(), file=self._fd)

        # enable garbage collection after we're done with measurments
        gc.enable()


uberlogs.install()
uber_logger = uberlogs.getLogger("uber")
std_logger = logging.getLogger("std")
p = Person(name="oded",
           age=26,
           favorite_colors=["green", "yellow"],
           single=False)

iterations = int(os.getenv("ITERATIONS", 1))

msg = "Profiling {} iterations".format(iterations)
print("{msg}\n{underline}".format(msg=msg,
                                  underline="-" * len(msg)),
      file=sys.stderr)

# run test with std logging using % formatting
old_simple_fmt = "Hey! my name is %s, my age is: %s & my most favorite color is: %s!"
with TimeIt(scope_name="std %", fd=sys.stderr):
    for _ in range(iterations):
        std_logger.info(old_simple_fmt, p.name, p.age, p.favorite_colors[0])

# run test with std logging using .format() formatting
simple_fmt = "Hey! my name is {p_name}, my age is: {p_age} & my most favorite color is: {color}!"
with TimeIt(scope_name="std .format()", fd=sys.stderr):
    for _ in range(iterations):
        std_logger.info(simple_fmt.format(p_name=p.name,
                                          p_age=p.age,
                                          color=p.favorite_colors[0]))


# run test with uberlog using .format() formatting
with TimeIt(scope_name="uber .format()", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(simple_fmt, p_name=p.name,
                         p_age=p.age,
                         color=p.favorite_colors[0],
                         extra=dict(single=p.single))

# run test with uberlog using .format() formatting
complex_fmt = "Hey! my name is {person.name}, my age is: {person.age} & my most favorite color is: {person.favorite_colors[0]}!"
with TimeIt(scope_name="uber complex .format()", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(complex_fmt,
                         person=p,
                         extra=dict(single=p.single))


# run test with uberlog using .format() formatting, with statement evaluation
simple_statement_fmt = "Hey! my name is {p.name}, my age is: {p.age} & my most favorite color is: {p.favorite_colors[0]}!"
with TimeIt(scope_name="uber .format() with statement", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(simple_statement_fmt, extra=dict(single=p.single))


# run test with uberlog using .format() formatting, with statement evaluation
complex_statement_fmt = "Hey! my name is {p.name}, my age is: {p.age} & my most favorite color is: {person.favorite_colors[0]}!"
with TimeIt(scope_name="uber complex .format() with statement", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(complex_statement_fmt,
                         person=p,
                         extra=dict(single=p.single))
