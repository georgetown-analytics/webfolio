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
            Q(**{f"{relation}__faculty":faculty})
            for faculty in faculty
            for relation in self.REL_FIELDS
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
                qor.append(Q(advisor__cohort__cohort=cohort))
                qor.append(Q(instructor__course__cohort__cohort=cohort))
            else:
                qor.append(Q(advisor__cohort=cohort))
                qor.append(Q(instructor__course__cohort=cohort))

        query = qor[0]
        for item in qor[1:]:
            query |= item

        return self.filter(query)

    def roles(self):
        """
        Returns all the role values from the specified query
        """
        return chain(*[
            list(chain(*self.filter(content_type__model=field).values_list(f"{field}__role")))
            for field in self.REL_FIELDS
        ])


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
