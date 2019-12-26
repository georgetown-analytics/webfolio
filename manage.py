#!/usr/bin/env python
# manage
# Django's command-line utility for administrative tasks.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 09:27:55 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: manage.py [] benjamin@bengfort.com $

"""
Django's command-line utility for administrative tasks.
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import dotenv


DJANGO_SETTINGS_MODULE = "webfolio.settings"


##########################################################################
## Main Method
##########################################################################

def main():
    # load .env file
    dotenv.load_dotenv(dotenv.find_dotenv())

    # set default environment variables
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

     # execute the django admin script
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
