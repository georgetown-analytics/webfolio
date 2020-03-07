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
    email = models.EmailField(
        null=True, blank=True,
        help_text="Preferred contact email for faculty and students",
    )
    occupation = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Title or role of your non-Georgetown related occupation",
    )
    organization = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="The organization you work for outside of Georgetown",
    )
    bio = models.CharField(
        max_length=1000, null=True, blank=True,
        help_text="Short bio describing your data science activities",
    )
    github = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="Optional GitHub username (no url or @ symbol prefix)"
    )
    twitter = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="Optional Twitter username (no url or @ symbol prefix)"
    )
    linkedin = models.URLField(
        null=True, blank=True,
        help_text="Optional URL of your LinkedIn profile"
    )
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, default=0.0,
        help_text="Expected hourly rate of faculty, used for contract validation",
    )
    exclude = models.BooleanField(
        default=False, null=False,
        help_text="Exclude from active faculty participation (archive only)",
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

    def get_email(self):
        """
        Determines the email address of the faculty member based on preferences.
        """
        if self.email:
            return self.email
        if self.user.email:
            return self.user.email
        if self.netid:
            return "{}@georgetown.edu".format(self.netid)
        return None

    def primary_role(self):
        """
        Returns the most common assignment this faculty member has had.
        """
        # TODO: this hack is going to lead to poor performance
        roles = self.assignments.values('role').annotate(count=models.Count("role"))
        roles = roles.order_by("-count")[0:1]
        return FACULTY_ROLES[roles[0]["role"]]

    def gravatar(self, size=35):
        email = self.get_email() or ""
        email_hash = md5(str(email.strip().lower()).encode('utf-8')).hexdigest()
        url = "//www.gravatar.com/avatar/{0}?s={1}&d=identicon&r=PG"
        return url.format(email_hash, size)

    def __str__(self):
        return self.get_full_name()


##########################################################################
## Faculty Assignments
##########################################################################

class Assignment(TimeStampedModel):
    """
    Faculty assignments link instructors to a cohort either through a role (e.g.
    Capstone Advisor) or through a course (e.g. an instructional assignment).
    Assignments also generally have one contract associated with them (e.g. a completed
    contractual agreement with the faculty member). Courses taught by multiple
    instructors will have multiple assignments associated with them.
    """

    faculty = models.ForeignKey(
        "Faculty", on_delete=models.CASCADE, null=False, blank=False,
        related_name="assignments",
        help_text="Faculty member who is instructing a course or advising the cohort",
    )
    cohort = models.ForeignKey(
        "cohort.Cohort", on_delete=models.CASCADE, null=False, blank=True,
        related_name="instructional_assignments",
        help_text="Must specify if a course is not set, otherwise will default to course cohort",
    )
    course = models.ForeignKey(
        "cohort.Course", on_delete=models.CASCADE, null=True, blank=True, default=None,
        related_name="instructional_assignments",
        help_text="If the role is instructor, specify the course the faculty is teaching",
    )
    role = models.CharField(
        max_length=2, choices=FACULTY_ROLES, default=FACULTY_ROLES.Instructor,
        null=False, blank=True, help_text="The role of the faculty member in the cohort",
    )
    start = models.DateField(
        null=True, blank=True, default=None,
        help_text="The start date of the assignment (defaults to course/cohort start)",
    )
    end = models.DateField(
        null=True, blank=True, default=None,
        help_text="The end date of the assignment (defaults to course/cohort end)",
    )
    hours = models.PositiveSmallIntegerField(
        null=True, blank=True, default=None,
        help_text="The number of instructional hours assigned to the advisor (defaults to course hours)",
    )
    effort = models.PositiveSmallIntegerField(
        null=True, blank=True, default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percent of effort/responsibility the instructor is assigned",
    )
    primary = models.BooleanField(
        default=True, null=False,
        help_text="If this instructor has primary responsibility for the course or advisor role"
    )

    # Use a custom manager for better queries
    objects = AssignmentManager()

    class Meta:
        db_table = "assignments"
        ordering = ("-start", "-cohort__cohort")
        unique_together = ("faculty", "cohort", "course", "role")

    @property
    def is_instructor(self):
        """
        Any role can be an "instructional role" (e.g. TA), but this is only an
        instructional assignment if there is a course associated with it.
        """
        return self.course is not None

    def __str__(self):
        if self.is_instructor:
            s = f"{self.faculty} teaching {self.course}"
        else:
            s = f"{self.faculty} Cohort {self.cohort.cohort} {self.get_role_display()}"

        if self.effort and self.effort != 100:
            s += f" ({self.effort}%)"
        return s
