# cohort.models
# Cohort app database models.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 15:06:39 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: models.py [] benjamin@bengfort.com $

"""
Cohort app database models.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel


SEMESTER = Choices(
    ("SP", "Spring", "Spring"),
    ("SU", "Summer", "Summer"),
    ("FA", "Fall", "Fall"),
)


##########################################################################
## Cohorts
##########################################################################

class Cohort(TimeStampedModel):
    """
    A cohort represents a single group of data science students that conduct all of
    their coursework together throughout a semester and finish their capstones.
    """

    cohort = models.PositiveSmallIntegerField(
        null=False, blank=False, unique=True,
        help_text="The cohort number, e.g. which cohort from the beginning of the program"
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTER, null=False, blank=False,
        help_text="The academic semester the cohort has been assigned to",
    )
    start = models.DateField(
        null=True, blank=True,
        help_text="Date that the cohort starts, e.g. the first day of Foundations",
    )
    end = models.DateField(
        null=True, blank=True,
        help_text="Date that the cohort ends, e.g. the last day of Applied",
    )

    class Meta:
        db_table = "cohorts"
        ordering = ("-cohort",)

    def faculty(self):
        """
        Yields all faculty members associated with the cohort.
        """
        for fa in self.faculty_assignments():
            yield fa.faculty

    def faculty_assignments(self):
        """
        Yields all faculty assignments, starting with advisors then instructors.
        """
        for advisor in self.advisors.all():
            yield advisor

        for course in self.courses.all(select_related=True):
            for instructor in course.instructors.all():
                yield instructor

    def get_semester_display(self):
        if not self.start:
            return SEMESTER[self.semester].title()

        year = self.start.strftime("%Y")
        return "{} {}".format(SEMESTER[self.semester].title(), year)

    def __str__(self):
        if self.start:
            return "Cohort {} ({})".format(self.cohort, self.get_semester_display())
        return "Cohort {}".format(self.cohort)


##########################################################################
## Classes
##########################################################################

class Course(TimeStampedModel):
    """
    To keep things simple, a course represents a course that is delivered during a
    cohort (rather than a course offering). The course ID is unique and can be used to
    group by all instances of the same course, even if the title has changed.
    """

    cohort = models.ForeignKey("Cohort",
        null=False, blank=False, on_delete=models.CASCADE, related_name="courses",
        help_text="The cohort taking this course",
    )
    course_id = models.CharField(
        max_length=55, null=False, blank=False, db_index=True, verbose_name="Course ID",
        help_text="The course ID, e.g. XBUS-500 that uniquely identifies an offering",
    )
    section = models.PositiveSmallIntegerField(
        null=False, blank=False,
        help_text="The course section, should be unique with course_id",
    )
    title = models.CharField(
        max_length=255, null=False, blank=False,
        help_text="The full title of the course in the semester it's offered",
    )
    hours = models.PositiveSmallIntegerField(
        null=True, blank=True, default=12,
        help_text="The number of hours in the course, e.g. the CEUs",
    )
    start = models.DateField(
        null=True, blank=True,
        help_text="Date that the course starts, e.g. the first day of of the course",
    )
    end = models.DateField(
        null=True, blank=True,
        help_text="Date that the course ends, e.g. the last day of the course",
    )
    instructors = models.ManyToManyField(
        "faculty.Faculty", through="faculty.Instructor", related_name="courses",
    )

    class Meta:
        db_table = "courses"
        ordering = ("-cohort__cohort", "start")
        unique_together = ("course_id", "section")

    def __str__(self):
        return "{} -- {}".format(self.title, self.cohort)


##########################################################################
## Capstone
##########################################################################

class Capstone(TimeStampedModel):
    """
    Represents a capstone project completed by students in a cohort. Used to organize
    and manage capstones on the site.
    """

    cohort = models.ForeignKey("Cohort",
        null=False, blank=False, on_delete=models.CASCADE, related_name="capstones",
        help_text="The cohort the capstone was completed in",
    )
    title = models.CharField(
        max_length=255, null=False, blank=False,
        help_text="The full title of the capstone project",
    )

    class Meta:
        db_table = "capstones"
        ordering = ("-cohort",)

    def __str__(self):
        return "{} ({})".format(self.title, self.cohort)
