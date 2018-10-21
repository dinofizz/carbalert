import os

from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Unable to find environment variable: " + var_name
        raise ImproperlyConfigured(error_msg)
