from collections import namedtuple

import uberlogs
uberlogs.install()

logger = uberlogs.getLogger("test")

Person = namedtuple('Person', ['name', 'age'])
p = Person(name="oded", age=26)


logger.debug("Hey! my name is {p_name}, and my age is: {p_age}!",
             p_name=p.name, p_age=p.age)

logger.info("Hey! my name is {p.name}, and my age is: {p.age}!")

logger.warning("Hey! my name is {p.name}, and my age is: {p.age}!",
               extra=dict(motto="hakuna matata"))
