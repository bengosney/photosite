# Locals
from .base import *  # noqa
from .base import BASE_DIR, INSTALLED_APPS

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^ukj0@=vmemq^ljcsj$=1%)w!(et856olsn&ig6k*m#4hjzkk&"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += [
    "bakery",
    "wagtailbakery",
]

BUILD_DIR = BASE_DIR + "/build/"

BAKERY_VIEWS = ("wagtailbakery.views.AllPublishedPagesView",)

BAKERY_GZIP = True

try:
    # Locals
    from .local import *  # noqa
except ImportError:
    pass
