# cohort.apps
# Cohort apps and configuration
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 15:06:39 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: apps.py [] benjamin@bengfort.com $

"""
Cohort apps and configuration
"""

##########################################################################
## Imports
##########################################################################

from django.apps import AppConfig


class CohortConfig(AppConfig):
    name = 'cohort'
