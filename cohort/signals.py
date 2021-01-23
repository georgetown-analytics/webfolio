# cohort.signals
# Signals used by cohort models - imported by the apps.py configuration.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Jan 03 12:09:27 2020 -0500
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: signals.py [] benjamin@bengfort.com $

"""
Signals used by cohort models - imported by the apps.py configuration.
"""

##########################################################################
## Imports
##########################################################################

from django.dispatch import receiver
from django.db.models.signals import pre_save

from cohort.models import Course


@receiver(pre_save, sender=Course, dispatch_uid="check_course_defaults")
def check_course_defaults(sender, instance, **kwargs):
    # Ensure that the cohort and instance semesters are the same
    if not instance.semester and instance.cohort:
        instance.semester = instance.cohort.semester
