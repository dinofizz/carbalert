from carbalert.carbalert.env_var_helper import get_env_variable
from .base import *

SECRET_KEY = get_env_variable("SECRET_KEY")

DEBUG = False

WSGI_APPLICATION = "carbalert.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "HOST": "db",
        "PORT": 5432,
    }
}
