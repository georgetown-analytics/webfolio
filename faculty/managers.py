# faculty.managers
# Query managers for faculty models.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Dec 30 15:59:03 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: managers.py [] benjamin@bengfort.com $

"""
Query managers for faculty models.
"""

##########################################################################
## Imports
##########################################################################

from itertools import chain
from django.db import models
from django.db.models import Q


##########################################################################
## Assignment Queryset and Manager
##########################################################################

class AssignmentQuerySet(models.QuerySet):

    REL_FIELDS = ("advisor", "instructor")

    def faculty(self, *faculty):
        """
        Filter the assignments based on the specified faculty members
        """
        if len(faculty) == 0:
            raise ValueError("specify at least one faculty to filter on")

        qor = [
            Q(faculty=faculty)
            for faculty in faculty
        ]
        query = qor[0]
        for item in qor[1:]:
            query |= item

        return self.filter(query)

    def cohort(self, *cohorts):
        """
        Filter the assignments based on the specified cohorts
        """
        if len(cohorts) == 0:
            raise ValueError("specify at least one cohort to filter on")

        qor = []
        for cohort in cohorts:
            if isinstance(cohort, int):
                qor.append(cohort__cohort=cohort)
            else:
                qor.append(Q(cohort=cohort))

        query = qor[0]
        for item in qor[1:]:
            query |= item

        return self.filter(query)

    def instructional(self):
        """
        Return only assignments that have associated courses.
        """
        return self.exclude(course__isnull=True)

    def advisors(self):
        """
        Return only assignments that do not have an associated course.
        """
        return self.exclude(course__isnull=False)


class AssignmentManager(models.Manager):

    def get_queryset(self):
        return AssignmentQuerySet(self.model, using=self._db)

    def faculty(self, *faculty):
        """
        Filter the assignments based on the specified faculty members
        """
        return self.get_queryset().faculty(*faculty)

    def cohort(self, *cohorts):
        """
        Filter the assignments based on the specified cohorts
        """
        return self.get_queryset().cohort(*cohorts)

    def instructional(self):
        """
        Return only assignments that have associated courses.
        """
        return self.get_queryset().instructional()

    def advisors(self):
        """
        Return only assignments that do not have an associated course.
        """
        return self.get_queryset().advisors()


##########################################################################
## Contacts Manager
##########################################################################

class ContactQuerySet(models.QuerySet):

    def primary(self):
        return self.filter(primary=True).exclude(archive=True)

    def active(self):
        return self.exclude(archive=True)


class ContactManager(models.Manager):

    def get_queryset(self):
        return ContactQuerySet(self.model, using=self._db)

    def primary(self):
        return self.get_queryset().primary()

    def active(self):
        return self.get_queryset().active()