"""
Django development settings for esite project.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/

This development settings are unsuitable for production, see
https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/
"""

from .base import *


#> Debug switch
# SECURITY WARNING: don't run with debug turned on in production!
# See https://docs.djangoproject.com/en/2.2/ref/settings/#debug
DEBUG = True

#> Secret key
# SECURITY WARNING: keep the secret key used in production secret!
# See https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key
SECRET_KEY = 'ct*z11t*ns876z)!f5f3h1byn7pp1ma5i!9*oo!=dmtmnrvzcn'

#> Allowed hosts
# Accept all hostnames, since we don't know in advance.
# See https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = '*'

#> Email backend
# The backend to use for sending emails.
# See https://docs.djangoproject.com/en/2.2/topics/email/#console-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2019 Werbeagentur Christian Aichner
