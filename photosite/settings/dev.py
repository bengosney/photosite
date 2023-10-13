# Locals
from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^ukj0@=vmemq^ljcsj$=1%)w!(et856olsn&ig6k*m#4hjzkk&"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    # Locals
    from .local import *  # noqa
except ImportError:
    pass
