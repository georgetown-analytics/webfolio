# webfolio.wsgi
# WSGI config for webfolio project.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 09:27:55 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: wsgi.py [] benjamin@bengfort.com $

"""
WSGI config for webfolio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

##########################################################################
## Imports
##########################################################################

import os
import dotenv

from django.core.wsgi import get_wsgi_application


##########################################################################
## WSGI Configuration
##########################################################################

# load .env file
dotenv.load_dotenv(dotenv.find_dotenv())

# set default environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webfolio.settings.development")

# export the wsgi application for import
application = get_wsgi_application()
