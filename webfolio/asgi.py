# webfolio.asgi
# ASGI config for webfolio project.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 09:27:55 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: asgi.py [] benjamin@bengfort.com $

"""
ASGI config for webfolio project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

##########################################################################
## Imports
##########################################################################

import os
import dotenv

from django.core.asgi import get_asgi_application


##########################################################################
## ASGI Configuration
##########################################################################

# load .env file
dotenv.load_dotenv(dotenv.find_dotenv())

# set default environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webfolio.settings")

# export the asgi application for import
application = get_asgi_application()
