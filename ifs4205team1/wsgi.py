"""
WSGI config for ifs4205team1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

import dotenv
from django.core.wsgi import get_wsgi_application

dotenv.read_dotenv((os.path.dirname(__file__), 'config', 'settings', '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifs4205team1.config.settings.production')

application = get_wsgi_application()
