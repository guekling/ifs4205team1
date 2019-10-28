# Development Settings

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nu32dq^3q)4eza_c8_585)6a*5n&8o3q=96^v!&36ac#+2)a5v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.environ.get("DB_NAME"),
    'USER': os.environ.get("DB_USER"),
    'PASSWORD': os.environ.get("DB_PASS"),
    'HOST': os.environ.get("DB_HOST"),
    'PORT': '5432',
  },
  'safedb': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.environ.get("DB_NAME2"),
    'USER': os.environ.get("DB_USER2"),
    'PASSWORD': os.environ.get("DB_PASS2"),
    'HOST': os.environ.get("DB_HOST2"),
    'PORT': '5432',
  },
  'logdb': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.environ.get("DB_NAME3"),
    'USER': os.environ.get("DB_USER3"),
    'PASSWORD': os.environ.get("DB_PASS3"),
    'HOST': os.environ.get("DB_HOST3"),
    'PORT': '5432',
  }
}

DATABASE_ROUTERS = [
  'researcherquery.router.ResearcherqueryRouter',
  'userlogs.router.UserlogsRouter'
]

# Media files

MEDIA_URL = os.environ.get("MEDIA_URL")