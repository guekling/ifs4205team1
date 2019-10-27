# Production Settings

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

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
    'OPTIONS': {
      'sslmode': 'verify-full',
      'sslcert': '/home/sadm/.postgresql/default.crt',
      'sslkey': '/home/sadm/.postgresql/default.key',
      'sslrootcert': '/home/sadm/.postgresql/default_root.crt',
    },
  },
  'safedb': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.environ.get("DB_NAME2"),
    'USER': os.environ.get("DB_USER2"),
    'PASSWORD': os.environ.get("DB_PASS2"),
    'HOST': os.environ.get("DB_HOST2"),
    'PORT': '5432',
    'OPTIONS': {
      'sslmode': 'verify-full',
      'sslcert': '/home/sadm/.postgresql/safedb.crt',
      'sslkey': '/home/sadm/.postgresql/safedb.key',
      'sslrootcert': '/home/sadm/.postgresql/safedb_root.crt',
    },
  },
  'logdb': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.environ.get("DB_NAME3"),
    'USER': os.environ.get("DB_USER3"),
    'PASSWORD': os.environ.get("DB_PASS3"),
    'HOST': os.environ.get("DB_HOST3"),
    'PORT': '5432',
    'OPTIONS': {
      'sslmode': 'verify-full',
      'sslrootcert': '/home/sadm/.postgresql/logdb_root.crt',
      'sslcert': '/home/sadm/.postgresql/logdb.crt',
      'sslkey': '/home/sadm/.postgresql/logdb.key',
    },
  }
}

DATABASE_ROUTERS = [
  'researcherquery.router.ResearcherqueryRouter',
  'userlogs.router.UserlogsRouter'
]

# Logging

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    # Send all messages to file
    'FILE_CONSOLE': {
      'level': 'INFO',
      'class': 'logging.FileHandler',
      'filename': os.path.join(BASE_DIR, 'logs', 'console.log'),
    },
  },
  'loggers': {
    'root': {
      'handlers': ['FILE_CONSOLE'],
      'level': 'DEBUG',
      'propagate': True,
    },
  },
}

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True