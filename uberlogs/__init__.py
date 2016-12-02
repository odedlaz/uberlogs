from six.moves import builtins

# the overhead of the following stub is negligent
# compared to the overhead uberlog adds

if not hasattr(builtins, 'profile'):
    from functools import wraps

    def profile(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    builtins.profile = profile

from .formatters import *
from .handlers import *
from .public import getLogger, install
