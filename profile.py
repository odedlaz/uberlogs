from __future__ import print_function
import os
import sys
import time
from six.moves import range
from collections import namedtuple
import logging
import uberlogs
uberlogs.install()


logger = uberlogs.getLogger("test")
std_logger = logging.getLogger("stdtest")

Person = namedtuple('Person', ['name', 'age'])
p = Person(name="oded", age=26)


starttime = time.time()

for _ in range(int(os.getenv("ITERATIONS", 1))):
    std_logger.error(
        "Hey! my name is {name}, and I'm not uber".format(name="bibi"))
    logger.debug("Hey! my name is {p_name}, and my age is: {p_age}!",
                 p_name=p.name, p_age=p.age)

    logger.info("Hey! my name is {p.name}, and my age is: {p.age}!")

    logger.warning("Hey! my name is {p.name}, and my age is: {p.age}!",
                   extra=dict(motto="hakuna matata"))

print('test took {} seconds to run'.format(time.time() - starttime),
      file=sys.stderr)
