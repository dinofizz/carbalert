from .base import *
import os
import django

# We load this here and not directly via a "pre-set" environment variable because of path weirdness when Django
# starts-up via the celery fixup.
os.environ["DJANGO_SETTINGS_MODULE"] = "carbalert.carbalert.settings.development"

django.setup()
