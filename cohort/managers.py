# cohort.managers
# Query managers for cohort models.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Dec 29 16:02:54 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: managers.py [] benjamin@bengfort.com $

"""
Query managers for cohort models.
"""

##########################################################################
## Imports
##########################################################################

from datetime import date
from django.db import models


##########################################################################
## Time Range Queryset and Manager
##########################################################################

class TimeRangeQuerySet(models.QuerySet):

    def starts_after(self, day):
        """
        Include objects that starts after the specified day
        """
        return self.filter(start__gt=day)

    def ends_after(self, day):
        """
        Include objects that ends after the specified day
        """
        return self.filter(end__gt=day)

    def starts_before(self, day):
        """
        Include objects that starts before the specified day
        """
        return self.filter(start__lt=day)

    def ends_before(self, day):
        """
        Include objects that end before the specified day
        """
        return self.filter(end__lt=day)

    def completed(self):
        """
        Include only objects that have been completed.
        """
        return self.ends_before(self.today())

    def current(self):
        """
        Include only objects that are currently active.
        """
        today = date.today()
        return self.filter(start__lte=today, end__gte=today)

    def upcomming(self):
        """
        Include only objects that are scheduled to occur in the future.
        """
        return self.starts_after(date.today())


class TimeRangeManager(models.Manager):

    def get_queryset(self):
        return TimeRangeQuerySet(self.model, using=self._db)

    def completed(self):
        """
        Include only objects that have been completed.
        """
        return self.get_queryset().completed()

    def current(self):
        """
        Include only objects that are currently active.
        """
        return self.get_queryset().current()

    def upcomming(self):
        """
        Include only objects that are scheduled to occur in the future.
        """
        return self.get_queryset().upcomming()


##########################################################################
## Cohort Queryset and Manager
##########################################################################

class CohortQuerySet(TimeRangeQuerySet):
    pass


class CohortManager(TimeRangeManager):

    def get_queryset(self):
        return CohortQuerySet(self.model, using=self._db)


##########################################################################
## Courses Queryset and Manager
##########################################################################

class CourseQuerySet(TimeRangeQuerySet):
    pass


class CourseManager(TimeRangeManager):

    def get_queryset(self):
        return CohortQuerySet(self.model, using=self._db)