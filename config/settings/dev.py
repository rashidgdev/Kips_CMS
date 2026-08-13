from .base import *  # noqa: F401,F403

DEBUG = True

# Extends (not replaces) the env-driven ALLOWED_HOSTS from base.py, so
# DJANGO_ALLOWED_HOSTS in .env (e.g. a LAN IP for testing the mobile app on
# a physical device) actually takes effect instead of being overwritten.
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS) | {'localhost', '127.0.0.1'})  # noqa: F405

INTERNAL_IPS = ['127.0.0.1']
