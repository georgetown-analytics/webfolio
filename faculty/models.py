# faculty.models
# Faculty app database models.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 16:06:48 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: models.py [] benjamin@bengfort.com $

"""
Faculty app database models.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models
from model_utils import Choices
from django.conf import settings
from model_utils.models import TimeStampedModel
from django.core.validators import MaxValueValidator, MinValueValidator


FACULTY_ROLES = Choices(
    ("IN", "Instructor", "Instructor"),
    ("TA", "TA", "Teaching Assistant"),
    ("CA", "Advisor", "Capstone Advisor"),
    ("FD", "Director", "Faculty Director"),
    ("SE", "SME", "Subject Matter Expert"),
)


##########################################################################
## Faculty Model
##########################################################################

class Faculty(TimeStampedModel):
    """
    Contains faculty-member specific information and can be linked to a specific user
    if necessary. Faculty can be assigned to courses and roles for each cohort.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="The user associated with the faculty member (optional)",
    )
    netid = models.CharField(
        max_length=24, null=True, blank=True,
        help_text="The Georgetown NetID of the faculty member",
    )
    first_name = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="The first name of the faculty, if not set the user is used",
    )
    last_name = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="The last name of the faculty, if not set the user is used",
    )
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, default=0.0,
        help_text="Expected hourly rate of faculty, used for contract validation",
    )

    class Meta:
        db_table = "faculty"
        ordering = ("last_name", "first_name")
        verbose_name = "faculty"
        verbose_name_plural = "faculty members"

    def get_full_name(self):
        fn = " ".join([self.first_name, self.last_name]).strip()
        if not fn and self.user is not None:
            return self.user.get_full_name()
        return fn


##########################################################################
## Faculty Assignments
##########################################################################

class Instructor(TimeStampedModel):
    """
    A faculty assignment to teach a specific class or workshop. This is a different
    from a TA or Capstone advising assignment since it directly links faculty members
    to courses along with their instructional responsibility.
    """

    course = models.ForeignKey(
        "cohort.Course", on_delete=models.CASCADE, null=False, blank=False,
        related_name="instructional_assignments",
        help_text="The course the faculty is being assigned to",
    )
    faculty = models.ForeignKey(
        "Faculty", on_delete=models.CASCADE, null=False, blank=False,
        related_name="instructional_assignments",
        help_text="The faculty member that is instructing the course",
    )
    effort = models.PositiveSmallIntegerField(
        null=False, blank=True, default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percent of effort/responsibility the instructor is assigned",
    )
    primary = models.BooleanField(
        default=True, null=False,
        help_text="If this instructor has primary responsibility for the course"
    )
    role = models.CharField(
        max_length=2, choices=FACULTY_ROLES, default=FACULTY_ROLES.Instructor,
        null=False, blank=True, help_text="The role of the faculty member in the cohort",
    )

    class Meta:
        db_table = "instructors"
        ordering = ("-course__start",)
        unique_together = ("course", "faculty")


class Advisor(TimeStampedModel):
    """
    A faculty assignment to provide instructional support throughout a cohort. This is
    different from an instructional role because the
    """

    cohort = models.ForeignKey(
        "cohort.Cohort", on_delete=models.CASCADE, null=False, blank=False,
        related_name="advisors", help_text="The cohort the faculty is being assigned to",
    )
    faculty = models.ForeignKey(
        "Faculty", on_delete=models.CASCADE, null=False, blank=False,
        help_text="The faculty member that is advising the cohort",
    )
    role = models.CharField(
        max_length=2, choices=FACULTY_ROLES, null=False, blank=True,
        help_text="The role of the faculty member in the cohort",
    )
    hours = models.PositiveSmallIntegerField(
        null=False, blank=True, default=30,
        help_text="The number of instructional hours assigned to the advisor",
    )
    effort = models.PositiveSmallIntegerField(
        null=False, blank=True, default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percent of effort/responsibility the advisor is assigned",
    )
    primary = models.BooleanField(
        default=True, null=False,
        help_text="If this advisor has primary responsibility for the cohort"
    )

    class Meta:
        db_table = "advisors"
        ordering = ("-cohort__start",)
        unique_together = ("cohort", "faculty", "role")
