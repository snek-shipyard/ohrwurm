"""
Django development settings for esite project.

For more information on this file, see
https://docs.djangoproject.com/en/stable/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/stable/ref/settings/

This development settings are unsuitable for production, see
https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
"""

from .base import *

# > Debug Switch
# SECURITY WARNING: don't run with debug turned on in production!
# See https://docs.djangoproject.com/en/stable/ref/settings/#debug
DEBUG = True

# > Secret Key
# SECURITY WARNING: keep the secret key used in production secret!
# See https://docs.djangoproject.com/en/stable/ref/settings/#secret-key
SECRET_KEY = "ct*z11t*ns876z)!f5f3h1byn7pp1ma5i!9*oo!=dmtmnrvzcn"

# > Allowed Hosts
# Accept all hostnames, since we don't know in advance.
# See https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts
ALLOWED_HOSTS = "*"

# > Email Backend
# The backend to use for sending emails.
# See https://docs.djangoproject.com/en/stable/topics/email/#console-backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# > Set Base_Url
# Set the base url, needed to acces wagtail.
# See https://docs.wagtail.io/en/v0.8.10/howto/settings.html
BASE_URL = "http://localhost:8000"

TELEGRAM_API_ID = "1349666"
TELEGRAM_API_HASH = "234cdd3f30e0b5f7d5052209e3c10b31"
TELEGRAM_BOT_TOKEN = "1121882585:AAGH4MGYFegk1mXaQwJRWGvzknhOQq57Ez0"

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019-2020 Simon Prast
