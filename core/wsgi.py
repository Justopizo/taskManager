"""WSGI config for the core project."""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
# Wrap with WhiteNoise to ensure static files are served even if middleware
# ordering or deployment nuances prevent automatic serving.
application = WhiteNoise(application, root=os.path.join(os.path.dirname(os.path.dirname(__file__)), "staticfiles"))
