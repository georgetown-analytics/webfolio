# webfolio.settings.development
# Configuration for the development environment.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sun Dec 29 20:01:44 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: development.py [] benjamin@bengfort.com $

"""
Configuration for the development environment.
"""

##########################################################################
## Imports
##########################################################################

import os
from .base import *  # noqa
from .base import PROJECT


##########################################################################
## Development Environment
##########################################################################

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

MEDIA_ROOT = os.path.join(PROJECT, 'tmp', 'media')

## Static files served by WhiteNoise nostatic server
STATIC_ROOT = os.path.join(PROJECT, 'tmp', 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Debugging email without SMTP
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(PROJECT, "outbox")
