# Testing Settings

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nu32dq^3q)4eza_c8_585)6a*5n&8o3q=96^v!&36ac#+2)a5v'

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

PROTECTED_MEDIA_URL = 'protected_media/'
PROTECTED_MEDIA_PATH = 'protected_media/'

# Admin page

ADMIN_URL = 'admin/'