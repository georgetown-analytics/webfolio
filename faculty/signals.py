# faculty.signals
# Signals used by faculty models - imported by the apps.py configuration.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Dec 30 16:39:09 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: signals.py [] benjamin@bengfort.com $

"""
Signals used by faculty models - imported by the apps.py configuration.
"""

##########################################################################
## Imports
##########################################################################

from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.signals import user_logged_in

from faculty.models import Faculty, Assignment


@receiver(pre_save, sender=Assignment, dispatch_uid="check_assignment_defaults")
def check_assignment_defaults(sender, instance, **kwargs):
    """
    Ensure that the assignment defaults are correctly set from blank fields before save.
    """
    # This does not validate, it just assigns the cohort to the course cohort if it can
    if not instance.cohort and instance.course is not None:
        instance.cohort = instance.course.cohort

    # Assign the start date of the assignment to the course or cohort default.
    if not instance.start:
        if instance.course is not None:
            instance.start = instance.course.start
        elif instance.cohort is not None:
            instance.start = instance.cohort.start

    # Assign the end date of the assignment to the course or cohort default.
    # This must be separate from start to ensure that the default is used correctly.
    if not instance.end:
        if instance.course is not None:
            instance.end = instance.course.end
        elif instance.cohort is not None:
            instance.end = instance.cohort.end

    # Assign the number of hours if available on the course
    if not instance.hours and instance.course is not None:
        instance.hours = instance.course.hours




@receiver(user_logged_in)
def associate_faculty_profile(sender, user, request, **kwargs):
    # Check if user has an associated faculty member
    if not hasattr(user, "faculty") or user.faculty is None:
        # Search for faculty
        query = Q(netid=user.username) | (Q(first_name=user.first_name) & Q(last_name=user.last_name))
        query = Faculty.objects.filter(query)
        if query.count() == 1:
            profile = query.first()
            user.faculty = profile
            user.save()

            changed = False
            if not profile.netid:
                profile.netid = user.username
                changed = True

            if not profile.email:
                profile.email = user.email
                changed = True

            if changed:
                profile.save()
