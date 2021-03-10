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

import pytz
import uuid

from django.db import models
from model_utils import Choices
from django.utils.timezone import is_aware
from model_utils.models import TimeStampedModel
from datetime import date, datetime, time, timedelta
from cohort.managers import CohortManager, CourseManager


SEMESTER = Choices(
    ("SP", "Spring", "Spring"),
    ("SU", "Summer", "Summer"),
    ("FA", "Fall", "Fall"),
)

SECTION = Choices("A", "B", "C")
SCS_ADDRESS = (
    "Georgetown University School of Continuing Studies, "
    "640 Massachusetts Ave NW, Washington, DC 20001"
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
        help_text="The cohort number, e.g. cohort count from the start of the program"
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTER, null=False, blank=False,
        help_text="The academic semester the cohort has been assigned to",
    )
    section = models.CharField(
        max_length=1, null=True, blank=True, choices=SECTION, default=None,
        help_text="If multiple cohorts per semester, the semester section",
    )
    start = models.DateField(
        null=True, blank=True, default=None,
        help_text="Date that the cohort starts, e.g. the first day of Foundations",
    )
    end = models.DateField(
        null=True, blank=True, default=None,
        help_text="Date that the cohort ends, e.g. the last day of Applied",
    )
    faculty = models.ManyToManyField(
        "faculty.Faculty", through="faculty.Assignment", related_name="cohorts",
    )

    # Add a custom manager to easily select cohorts by time
    objects = CohortManager()

    class Meta:
        db_table = "cohorts"
        ordering = ("-cohort",)

    def get_semester_display(self):
        """
        Effective string representation of the Semester
        """
        year = ""
        if self.start:
            year = self.start.strftime("%Y")

        sem = "{} {} {}".format(SEMESTER[self.semester], year, self.section or "")
        return sem.strip().replace("  ", " ")

    def percent_complete(self):
        """
        The percent of the days in the cohort that have been completed.
        """
        tdays = (self.end - self.start).days
        cdays = (date.today() - self.start).days
        if cdays < 0:
            return 0
        if cdays >= tdays:
            return 100
        return int((cdays / tdays) * 100)

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

    cohort = models.ForeignKey(
        "Cohort",
        null=True, blank=True, default=None,
        on_delete=models.CASCADE, related_name="courses",
        help_text="The cohort that this course is a part of (if data science)",
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTER, null=False, blank=True,
        help_text="The academic semester the course is in (cohort semester by default)",
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
        "faculty.Faculty", through="faculty.Assignment", related_name="courses",
    )

    # Add a custom manager to easily select courses by time
    objects = CourseManager()

    class Meta:
        db_table = "courses"
        ordering = ("-cohort__cohort", "start")
        unique_together = ("course_id", "section")

    def get_semester_display(self):
        """
        Effective string representation of the Semester
        """
        if self.cohort:
            return self.cohort.get_semester_display()

        year = ""
        if self.start:
            year = self.start.strftime("%Y")

        sem = f"{SEMESTER[self.semester].title()} {year}"
        return sem.strip()

    def make_calendar_events(self):
        """
        Creates calendar events for the course using a simple heuristic.

        If the calendar events cannot be created a ValueError is raised.
        """
        if self.calendar_events.count() > 0:
            raise ValueError(
                "cannot make calendar events when they already exist for this course, "
                "please update existing calendar events."
            )

        if self.start is None or self.end is None:
            raise ValueError("cannot create events without start and end dates")

        events = []
        if self.hours <= 6:
            if self.start != self.end:
                raise ValueError(
                    "cannot create multi-day events for courses <= 6 hours"
                )

            # If it is a 3 hour event, assume 6:30 - 9:30 pm
            if self.hours == 3:
                start = datetime(
                    self.start.year, self.start.month, self.start.day, 18, 30
                )
            # If it is a 6 hour event, assume 9:00 am - 4:00 pm
            elif self.hours == 6:
                start = datetime(
                    self.start.year, self.start.month, self.start.day, 9, 0
                )
            else:
                raise ValueError("cannot handle {} hours courses".format(self.hours))

            # Create the single day event
            events.append(CalendarEvent(
                start=start, end=start + timedelta(hours=self.hours)
            ))

        elif self.hours == 12:
            # Create 9 am - 4 pm events for both the start and end dates
            for day in (self.start, self.end):
                if day.weekday() != 5:
                    raise ValueError("can only create 12 hour courses on Saturdays")
                events.append(CalendarEvent(
                    start=datetime(day.year, day.month, day.day, 9, 0),
                    end=datetime(day.year, day.month, day.day, 16, 0),
                ))
        elif self.hours == 18:
            # Create 6:30 - 9:30 pm events for the fridays
            fridays = (self.start, self.end - timedelta(days=1))
            for day in fridays:
                if day.weekday() != 4:
                    raise ValueError(
                        "could not determine Friday evening for 18 hour course"
                    )
                events.append(CalendarEvent(
                    start=datetime(day.year, day.month, day.day, 18, 30),
                    end=datetime(day.year, day.month, day.day, 21, 30),
                ))

            # Create 9 am - 4pm events for the saturdays
            saturdays = (self.start + timedelta(days=1), self.end)
            for day in saturdays:
                if day.weekday() != 5:
                    raise ValueError("could not determine Saturday for 18 hour course")
                events.append(CalendarEvent(
                    start=datetime(day.year, day.month, day.day, 9, 0),
                    end=datetime(day.year, day.month, day.day, 16, 0),
                ))
        else:
            raise ValueError("cannot handle {} hours courses".format(self.hours))

        for event in events:
            event.summary = self.title
            event.location = SCS_ADDRESS
            event.course = self
            event.description = str(self)

            # Ensure start and end time are timezone aware -- above are in DC timezone
            ET = pytz.timezone(TIMEZONES[TIMEZONES.Eastern])
            event.start = ET.localize(event.start)
            event.end = ET.localize(event.end)

            # Save the event before we can add attendees
            event.save()

            # add the instructors as attendees
            for instructor in self.instructors.all():
                event.attendees.add(instructor)

        # Return fully populated calendar events
        return self.calendar_events.all()

    def __str__(self):
        if self.cohort:
            return f"{self.title} -- {self.cohort}"
        return f"{self.title} -- {self.get_semester_display()}"


##########################################################################
## Capstone
##########################################################################

class Capstone(TimeStampedModel):
    """
    Represents a capstone project completed by students in a cohort. Used to organize
    and manage capstones on the site.
    """

    cohort = models.ForeignKey(
        "Cohort",
        null=False, blank=False, on_delete=models.CASCADE,
        related_name="capstones",
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


##########################################################################
## Calendar Events
##########################################################################

TIMEZONES = Choices(
    ("E", "Eastern", "America/New_York"),
    ("C", "Central", "America/Chicago"),
    ("M", "Mountain", "America/Denver"),
    ("P", "Pacific", "America/Los_Angeles"),
)


class CalendarEvent(TimeStampedModel):
    """
    A calendar event connects course days to Google Calendar and also implements
    scheduling functionality in the app. The start and end time of the course should
    supercede calendar events and good code will ensure that any calendar events get
    updated/cleaned up when course information is changed.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    summary = models.CharField(
        max_length=255, null=False, blank=True, default="",
        help_text="Title to use for the event (by default the course title)"
    )
    location = models.CharField(
        max_length=255, null=False, blank=True, default="",
        help_text="Location to specify for the event (by default the SCS address)"
    )
    description = models.CharField(
        max_length=2000, null=False, blank=True, default="",
        help_text="Extra text describing the event"
    )
    start = models.DateTimeField(
        null=True, blank=True, default=None,
        help_text="Date and time the calendar event starts",
    )
    end = models.DateTimeField(
        null=True, blank=True, default=None,
        help_text="Date and time the calendar event ends",
    )
    timezone = models.CharField(
        max_length=1, null=False, default=TIMEZONES.Eastern, choices=TIMEZONES,
        help_text="The time zone of both the start and end time",
    )
    is_holiday = models.BooleanField(
        default=False,
        help_text="If the event is an academic holiday (schedule blocked)",
    )
    attendees = models.ManyToManyField(
        "faculty.Faculty", related_name="calendar_events", blank=True,
        help_text="Faculty members attending this event",
    )
    course = models.ForeignKey(
        "cohort.Course", on_delete=models.CASCADE, null=True, blank=True,
        related_name="calendar_events",
        help_text="Optional course that is associated with this calendar event",
    )

    class Meta:
        db_table = "calendar"
        ordering = ("start",)
        get_latest_by = "start"
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"

    @property
    def event_id(self):
        """
        Events in the database can be tied to Google Calendar events using an ID
        that is a string that meets the following characteristics:

            - characters encoded in base32hex i.e. lowercase letters a-v and digits 0-9
            - length of the id is between 5 and 1024 characters
            - the id must be unique per calendar

        To simplify id creation and prevent collisions between calendars, we use a UUID
        as the primary key of this table. It is then serialized using base32hex encoding
        to interact with the Google Calendar API.

        ..seealso:: https://developers.google.com/calendar/v3/reference/events#id
        """
        return self.id.hex

    def json(self):
        """
        Returns the even in Google Calendar API json format.

        ..seealso:: https://developers.google.com/calendar/create-events
        """
        data = {
            "id": self.event_id,
            "summary": self.summary,
            "location": self.location,
            "description": self.description,
            "start": {},
            "end": {},
            "attendees": [],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "days": 5, "minutes": 0},
                    {"method": "popup", "days": 1, "minutes": 0},
                ],
            },
        }

        # Add the start and end to the json data
        for attr in ("start", "end"):
            dt = getattr(self, attr)
            if not dt:
                continue

            if is_aware(dt):
                dt = dt.astimezone(self.get_timezone_object())

            if self.is_all_day():
                data[attr] = {
                    "date": dt.strftime("%Y-%m-%d")
                }
            else:
                data[attr] = {
                    "dateTime": dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "timeZone": TIMEZONES[self.timezone],
                }

        # Add the attendees to the json data
        for attendee in self.attendees.all():
            email = attendee.get_email()
            if email:
                data["attendees"].append({
                    "email": email
                })

        return data

    def get_timezone_object(self):
        return pytz.timezone(TIMEZONES[self.timezone])

    def is_all_day(self):
        start = self.start.astimezone(self.get_timezone_object())
        return start.time() == time(0, 0)

    def saturday(self):
        """
        Returns the Saturday associated with the event, e.g. the start date if the start
        date is a Saturday, the day before if the start date is a Sunday, or the
        following Saturday if the start date is a weekday.
        """
        day = self.start.astimezone(self.get_timezone_object())

        if day.weekday() == 5:
            return day.date()
        elif day.weekday() < 5:
            return day.date() + timedelta(days=(5 - day.weekday() + 7) % 7)
        else:
            return day.date() - timedelta(days=1)

    def __str__(self):
        if self.is_holiday or self.is_all_day():
            return "{} ({})".format(self.summary, self.start.strftime("%Y-%m-%d"))
        return "{} ({} - {})".format(
            self.summary,
            self.start.strftime("%Y-%m-%d %H:%M"),
            self.end.strftime("%H:%M"),
        )
