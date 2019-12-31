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
from collections import Counter
from django.conf import settings
from faculty.managers import AssignmentManager
from model_utils.models import TimeStampedModel
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


FACULTY_ROLES = Choices(
    ("IN", "Instructor", "Instructor"),
    ("TA", "TA", "Teaching Assistant"),
    ("CA", "Advisor", "Capstone Advisor"),
    ("FD", "Director", "Faculty Director"),
    ("SE", "SME", "Subject Matter Expert"),
)

NAME_PREFIX = Choices(
    "Dr.", "Mr.", "Ms.", "Mrs.", "Dean", "Hon.", "Rev.",
)

NAME_SUFFIX = Choices(
    "PhD", "Esq", "MD", "LLD", "JD", "RN", "DO", "DDS", "CPA",
    "Jr.", "Sr.", "II", "III", "IV"
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
    prefix = models.CharField(
        max_length=4, null=True, blank=True, choices=NAME_PREFIX, default=None,
        help_text="Title or prefix for the faculty member's display name",
    )
    first_name = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="The first name of the faculty, if not set the user is used",
    )
    last_name = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="The last name of the faculty, if not set the user is used",
    )
    suffix = models.CharField(
        max_length=4, null=True, blank=True, choices=NAME_SUFFIX, default=None,
        help_text="Suffix for the faculty member's display name",
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
            fn = self.user.get_full_name()

        if self.prefix:
            fn = "{} {}".format(self.prefix, fn)
        if self.suffix:
            fn += ", " + self.suffix
        return fn

    def primary_role(self):
        """
        Returns the most common assignment this faculty member has had.
        """
        # TODO: this hack is going to lead to poor performance
        roles = Counter(Assignment.objects.faculty(self).roles())
        return FACULTY_ROLES[roles.most_common(1)[0][0]]

    def __str__(self):
        return self.get_full_name()


##########################################################################
## Faculty Assignments
##########################################################################

class Assignment(TimeStampedModel):
    """
    Assignments join both instructional and advisorial assignments and relate them to a
    single paid contract. This table uses ContentTypes to join the different assignment
    types into a single queryable model.
    """

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=False, blank=False,
        help_text="The model type of the assignment object, e.g. Instructor or Assignment",
    )
    object_id = models.PositiveSmallIntegerField(
        null=False, blank=False,
        help_text="The primary key of the assignment object."
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # Use a custom manager for better queries
    objects = AssignmentManager()

    class Meta:
        db_table = "assignments"
        ordering = ("-created",)
        unique_together = ("content_type", "object_id")

    def __str__(self):
        return str(self.content_object)


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
        null=True, blank=True, default=100,
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
    assignment = GenericRelation(Assignment, related_query_name="instructor")

    class Meta:
        db_table = "instructors"
        ordering = ("-course__start",)
        unique_together = ("course", "faculty")
        verbose_name = "Instructional assignment"

    def __str__(self):
        if self.effort and self.effort != 100:
            return "{} teaching {} ({}%)".format(self.faculty, self.course, self.effort)
        return "{} teaching {}".format(self.faculty, self.course)


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
        related_name="advisor_assignments",
        help_text="The faculty member that is advising the cohort",
    )
    role = models.CharField(
        max_length=2, choices=FACULTY_ROLES, null=False, blank=True,
        help_text="The role of the faculty member in the cohort",
    )
    hours = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="The number of instructional hours assigned to the advisor",
    )
    effort = models.PositiveSmallIntegerField(
        null=True, blank=True, default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percent of effort/responsibility the advisor is assigned",
    )
    primary = models.BooleanField(
        default=True, null=False,
        help_text="If this advisor has primary responsibility for the cohort"
    )
    assignment = GenericRelation(Assignment, related_query_name="advisor")

    class Meta:
        db_table = "advisors"
        ordering = ("-cohort__start",)
        unique_together = ("cohort", "faculty", "role")
        verbose_name = "Advising assignment"

    def __str__(self):
        if self.effort and self.effort != 100:
            return "{} Cohort {} {} ({}%)".format(self.faculty, self.cohort.cohort, self.get_role_display(), self.effort)
        return "{} Cohort {} {}".format(self.faculty, self.cohort.cohort, self.get_role_display())
