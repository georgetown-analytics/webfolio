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

from django.db import models
from django.db.models import Q
from django.db import connection

from datetime import datetime, date


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

    def upcoming(self):
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

    def upcoming(self):
        """
        Include only objects that are scheduled to occur in the future.
        """
        return self.get_queryset().upcoming()


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

    def semester(self, semester, year):
        return self.filter(Q(semester=semester) & Q(start__year=year))

    def non_cohort(self):
        return self.filter(cohort__isnull=True)


class CourseManager(TimeRangeManager):

    def get_queryset(self):
        return CourseQuerySet(self.model, using=self._db)

    def non_cohort_courses(self, semester, year):
        return self.filter(
            Q(semester=semester) & Q(start__year=year) & Q(cohort__isnull=True)
        )


def scheduled_semesters(after=None):
    """
    Returns all semesters with courses scheduled on or after the specified datetime.

    Parameters
    ----------
    after : datetime, optional
        Get all semesters scheduled after the specified date, otherwise use today.
    """
    query = (
        "SELECT DISTINCT c.semester, EXTRACT(YEAR FROM c.start) AS year "
        "FROM courses c WHERE c.end >= %s"
    )

    if after is None:
        after = date.today().strftime("%Y-%m-%d")
    else:
        if not isinstance(after, (datetime, date)):
            raise TypeError("after must be a datetime or date")
        after = after.strftime("%Y-%m-%d")

    with connection.cursor() as cursor:
        cursor.execute(query, [after])
        rows = cursor.fetchall()

    return rows
