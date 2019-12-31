# faculty.apps
# Faculty apps and configuration.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 16:06:48 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: apps.py [] benjamin@bengfort.com $

"""
Faculty apps and configuration.
"""

##########################################################################
## Imports
##########################################################################

from django.apps import AppConfig


##########################################################################
## AppConfig
##########################################################################

class FacultyConfig(AppConfig):

    name = 'faculty'

    def ready(self):
        import faculty.signals # noqa
