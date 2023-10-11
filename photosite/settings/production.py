DEBUG = False

try:
    # Locals
    from .local import *  # noqa
except ImportError:
    pass
