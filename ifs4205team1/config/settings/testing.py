# Testing Settings

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

if 'TRAVIS' in os.environ:
  DATABASES = {
      'default': {
          'ENGINE':   'django.db.backends.postgresql_psycopg2',
          'NAME':     'travisci',
          'USER':     'postgres',
          'PASSWORD': '',
          'HOST':     'localhost',
          'PORT':     '',
      }
  }

# Media files

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'