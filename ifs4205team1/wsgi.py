"""
WSGI config for ifs4205team1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

dotenv_path = os.path.join(os.path.dirname(__file__), 'config', 'settings', '.env')
load_dotenv(dotenv_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifs4205team1.config.settings.production')

application = get_wsgi_application()
