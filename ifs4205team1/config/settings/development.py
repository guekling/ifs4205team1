# Development Settings

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nu32dq^3q)4eza_c8_585)6a*5n&8o3q=96^v!&36ac#+2)a5v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Media files

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = os.environ.get("MEDIA_URL")