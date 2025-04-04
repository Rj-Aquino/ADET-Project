"""
ASGI config for ADET project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
import resource
resource.setrlimit(resource.RLIMIT_AS, (450 * 1024 * 1024, 450 * 1024 * 1024))  # Hard limit

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ADET.settings')

application = get_asgi_application()
