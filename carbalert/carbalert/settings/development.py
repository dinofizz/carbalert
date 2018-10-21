from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "d9_zuop-f_9ah(fc0_x^zl92y(s!^)$*j=8!15mtslnk_u04p9"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db'
    }
}