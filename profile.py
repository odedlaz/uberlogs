from __future__ import print_function
import os
import gc
import six
import sys
import time
import logging
import uberlogs
from six.moves import range
from collections import namedtuple, OrderedDict
Person = namedtuple('Person', ['name', 'age', 'favorite_colors', 'single'])
PYTHON_VERSION = "{0.major}.{0.minor}.{0.micro}".format(sys.version_info)


color_map = {
    'green': '\x1b[32m',
    'red': '\x1b[31m',
    'yellow': '\x1b[93m'
}


class TimeIt(object):
    scope_times = {}

    def __init__(self, scope_name="", compare_to=None, fd=sys.stdout):
        self._start = None
        self._fd = fd
        self._scope_name = scope_name
        self._compare_to = compare_to or self._scope_name
        self._fmt = 'block took {secs:.3f} seconds, {percent} {adj} than \'{compare}\' [{scope}]'

    def __enter__(self):
        # run the garbage collector
        # then disable it so it won't tamper with the measurments
        gc.collect()
        gc.disable()
        self._start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        now = time.time() - self._start
        self.scope_times[self._scope_name] = now
        diff = 1 - (now / self.scope_times[self._compare_to])
        adj = "faster" if diff >= 0 else "slower"

        color = 'green'
        if -0.1 < diff < 0:
            color = 'yellow'
        elif diff < 0:
            color = 'red'

        percent = "{color}{diff:.2f}%\x1b[0m".format(color=color_map[color],
                                                     diff=abs(diff))

        print(self._fmt.format(secs=now,
                               percent=percent,
                               adj=adj,
                               compare=self._compare_to,
                               scope=self._scope_name).strip(), file=self._fd)

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


msg = "Profiling {} iterations [python {}]".format(iterations,
                                                   PYTHON_VERSION)

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
simple_kwargs = dict(p_name=p.name,
                     p_age=p.age,
                     color=p.favorite_colors[0])

with TimeIt(scope_name="std .format()", compare_to="std %", fd=sys.stderr):
    for _ in range(iterations):
        std_logger.info(simple_fmt.format(**simple_kwargs))


# run test with uberlog using .format() formatting
with TimeIt(scope_name="uber .format()", compare_to="std .format()", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(simple_fmt, **simple_kwargs)

# run test with uberlog using .format() formatting
complex_fmt = "Hey! my name is {person.name}, my age is: {person.age} & my most favorite color is: {person.favorite_colors[0]}!"
with TimeIt(scope_name="uber complex .format()",
            compare_to="uber .format()",
            fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(complex_fmt, person=p)

# run test with uberlog using .format() formatting, with statement evaluation
simple_statement_fmt = "Hey! my name is {p.name}, my age is: {p.age} & my most favorite color is: {p.favorite_colors[0]}!"
with TimeIt(scope_name="uber .format() with statement", compare_to="std .format()", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(simple_statement_fmt)


# run test with uberlog using .format() formatting, with statement evaluation
complex_statement_fmt = "Hey! my name is {p.name}, my age is: {p.age} & my most favorite color is: {person.favorite_colors[0]}!"
with TimeIt(scope_name="uber complex .format() with statement", compare_to="uber .format() with statement", fd=sys.stderr):
    for _ in range(iterations):
        uber_logger.info(complex_statement_fmt, person=p)
