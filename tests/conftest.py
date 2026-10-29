"""Pytest configuration: boot Django with ColdFront's settings before tests.

ColdFront 2.x model classes resolve settings (e.g. ``FIELD_CHOICES``) at
import time, so ``django.setup()`` must run before any test module imports
the plugin package.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coldfront.config.settings")
os.environ.setdefault("SECRET_KEY", "testing")
os.environ.setdefault("ALLOWED_HOSTS", "*")
os.environ.setdefault("API_TOKEN_PEPPERS", "1=TEST-VALUE-DO-NOT-USE-TEST-VALUE-DO-NOT-USE-TEST-VALUE-DO-NOT-USE")

import django

django.setup()
