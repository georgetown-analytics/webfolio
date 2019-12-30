# webfolio.settings.testing
# Testing settings to enable testing on Travis with Django tests.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Dec 29 20:07:00 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: testing.py [] benjamin@bengfort.com $

"""
Testing settings to enable testing on Travis with Django tests.
"""

##########################################################################
## Imports
##########################################################################

import dj_database_url

from .base import *  # noqa
from .base import REST_FRAMEWORK


##########################################################################
## Test Settings
##########################################################################

## Hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

## Database Settings
## https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600),
}

DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['default']['TEST'] = {'NAME': 'gdsc_test'}


STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

## Content without side effects
MEDIA_ROOT = "/tmp/gdsc_test/media"
STATIC_ROOT = "/tmp/gdsc_test/static"

##########################################################################
## Django REST Framework
##########################################################################

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
)
