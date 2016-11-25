# UberLogs

Writing good, usable logs is not an easy task. Why work hard when you can use UberLogs?

UberLogs does all the dumb work you have to do, to make your logs easy to parse:

- Human Readable, parsable log lines (with or without color)
- Machine redable, parsable log lines for your favorite data cruncher
- Variable formatting, so you don't have to write .format(...) or % (...) ever again
- Statement evaluation like in Ruby, Koltin, Python 3.6, etc'
- Handler to violently kill the process when a log on a specific level has been written
- Automatic twisted log rewriting to python.logging

## Motivation

I rarely use any other logging appenders than the console one. Most of the time I send my logs to a data cruncher and write horrible regular expressions to parse the data.

To ease the pain, I started formatting my logs, so they'll be easy to parse: `<message>; arg1=arg1val; arg2=arg2val` But that meant I had to write the same format **everywhere**, and I found myself writing long, long log lines:

```python
import logging
from collections import namedtuple

Eatable = namedtuple('Eatable', ['name', 'flavor', 'location'])

logger = logging.getLogger("test")

eatable = Eatable(name="bagel",
                  flavor="salty",
                  location="tel-aviv")


logger.info("I'm eating a {thing}; location: {location}; flavor: {flavor}".format(thing=eatable.name,
                                                                                  location=eatable.location,
                                                                                  flavor=eatable.flavor))

# 1970-1-1 18:24:17,578 - test - INFO - I'm eating a bagel; flavor: salty; location: tel-aviv
```

I had to find a better, more concise way of doing the same - that way is UberLogs:

```python
import uberlogs
from collections import namedtuple

Eatable = namedtuple('Eatable', ['name', 'flavor', 'location'])

uberlogs.install()

logger = uberlogs.getLogger("test")

eatable = Eatable(name="bagel",
                  flavor="salty",
                  location="tel-aviv")

logger.info("I'm eating a {eatable.name}", extra=dict(flavor=eatable.flavor,
                                                      location=eatable.location))

# 1970-1-1 18:26:17,578 - test - INFO - I'm eating a bagel; flavor: salty; location: tel-aviv
```

## Example

If you run this code...

```python
from collections import namedtuple
import uberlogs

uberlogs.install(kill_on=uberlogs.level.CRITICAL)

logger = uberlogs.getLogger("test")

Person = namedtuple('Person', ['name', 'age'])
p = Person(name="oded", age=26)


# uberlogs processes variable formats in string.format(...) manner
logger.debug("Hey! my name is {p_name}, and my age is: {p_age}!",
             p_name=p.name, p_age=p.age)

# it can also implicitly evaluate statements like in ruby or python 3.6  
logger.info("Hey! my name is {p.name}, and my age is: {p.age}!")

# and it can even add extra information to logs, without explicitly telling it to!
logger.warning("Hey! my name is {p.name}, and my age is: {p.age}!",
               extra=dict(motto="hakuna matata"))

# this line will violently kill the application with a return code of 1
# The app will close AFTER all other handlers are done processing this lines
# and it'll flush all data to stdout and stderr before doing so
#
# this is a very import behavior for production applications
logger.critical("Hey! my name is {p.name} and critical logs close this app!")
```

You'll see this output:

```bash
1970-1-1 18:00:50,979 - test - DEBUG - Hey! my name is oded, and my age is: 26!
{
   "file": "test.py",
   "func": "<module>",
   "level": "DEBUG",
   "logger": "test",
   "message": "Hey! my name is oded, and my age is: 26!",
   "p_age": 26,
   "p_name": "oded",
   "time": "1970-1-1T18:00:50+00:00"
}
1970-1-1 18:00:50,979 - test - INFO - Hey! my name is oded, and my age is: 26!
{
   "file": "test.py",
   "func": "<module>",
   "level": "INFO",
   "logger": "test",
   "message": "Hey! my name is oded, and my age is: 26!",
   "p_age": 26,
   "p_name": "oded",
   "time": "1970-1-1T18:00:50+00:00"
}
1970-1-1 18:00:50,980 - test - WARNING - Hey! my name is oded, and my age is: 26!; motto: hakuna matata
{
   "file": "test.py",
   "func": "<module>",
   "level": "WARNING",
   "logger": "test",
   "message": "Hey! my name is oded, and my age is: 26!",
   "motto": "hakuna matata",
   "p_age": 26,
   "p_name": "oded",
   "time": "1970-1-1T18:00:50+00:00"
}
```

When you use UberLogs with the following configuration:

```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "json": {
      "()": "uberlogs.JsonFormatter",
      "indent": 3,
      "parse_text": true,
      "include_format_keywords": true
    },
    "concat": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
      "()": "uberlogs.ConcatFormatter",
      "delimiter": "; ",
      "operator": ": ",
      "log_in_color": true,
      "include_format_keywords": false,
      "parse_text": true
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "DEBUG",
      "formatter": "concat",
      "stream": "ext://sys.stdout"
    },
    "json_console": {
      "class": "logging.StreamHandler",
      "level": "DEBUG",
      "formatter": "json",
      "stream": "ext://sys.stdout"
    }
  },
  "loggers": {},
  "root": {
    "level": "DEBUG",
    "handlers": [
      "console",
      "json_console"
    ],
    "propagate": "no"
  }
}
```
