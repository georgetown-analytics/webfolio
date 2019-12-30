# webfolio.settings.production
# Configuration for the production environment.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sun Dec 29 20:05:01 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: production.py [] benjamin@bengfort.com $

"""
Configuration for the production environment.
"""

##########################################################################
## Imports
##########################################################################

import os
from .base import *  # noqa
from .base import PROJECT


##########################################################################
## Production Environment
##########################################################################

## Ensure debug mode is not running production
DEBUG = False

## Hosts
ALLOWED_HOSTS = [
    'georgetowndata.science',
    'gdsc-webfolio.herokuapp.com',
]

## Use SSL
SECURE_SSL_REDIRECT = True

## Static files served by WhiteNoise
STATIC_ROOT = os.path.join(PROJECT, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
