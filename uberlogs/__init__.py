__version__ = '0.0.12'

# NOQA -> silence flake8 warnings
from six.moves import builtins  # NOQA
from .formatters import *  # NOQA
from .handlers import *  # NOQA
from .public import getLogger, install  # NOQA
