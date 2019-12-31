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

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from faculty.models import Assignment, Instructor, Advisor
from django.contrib.contenttypes.models import ContentType


def create_assignment(sender, instance, created, **kwargs):
    """
    Create an generic assignment when a type-specific assignment is saved.
    """
    content_type = ContentType.objects.get_for_model(instance)

    # Don't use get_or_create to prevent multiple DB queries
    try:
        assignment = Assignment.objects.get(
            content_type=content_type, object_id=instance.id
        )
    except Assignment.DoesNotExist:
        assignment = Assignment(content_type=content_type, object_id=instance.id)

    assignment.created = instance.created
    assignment.modified = instance.modified
    assignment.save()


def delete_assignment(sender, instance, **kwargs):
    """
    Delete an generic assignment when a type-specific assignment is deleted.
    """
    content_type = ContentType.objects.get_for_model(instance)
    try:
        assignment = Assignment.objects.get(
            content_type=content_type, object_id=instance.id
        )
        assignment.delete()
    except Assignment.DoesNotExist:
        pass


@receiver(post_save, sender=Instructor, dispatch_uid="create_instructional_assignment")
def create_instructional_assignment(sender, instance, created, **kwargs):
    return create_assignment(sender, instance, created, **kwargs)


@receiver(post_save, sender=Advisor, dispatch_uid="create_advisor_assignment")
def create_advisor_assignment(sender, instance, created, **kwargs):
    return create_assignment(sender, instance, created, **kwargs)


@receiver(post_delete, sender=Instructor, dispatch_uid="delete_instructional_assignment")
def delete_instructional_assignment(sender, instance, **kwargs):
    return delete_assignment(sender, instance, **kwargs)


@receiver(post_delete, sender=Advisor, dispatch_uid="delete_advisor_assignment")
def delete_advisor_assignment(sender, instance, **kwargs):
    return delete_assignment(sender, instance, **kwargs)
