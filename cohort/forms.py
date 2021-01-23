# cohort.forms
# Forms for managing courses and scheduling
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Jan 23 14:08:49 2021 -0500
#
# Copyright (C) 2021 Georgetown University
# For license information, see LICENSE.txt
#
# ID: forms.py [] benjamin@bengfort.com $

"""
Forms for managing courses and scheduling
"""

##########################################################################
## Imports
##########################################################################

from django import forms
from django.apps import apps
from datetime import timedelta
from collections import Counter
from django.contrib import messages


DTFMT = "%A, %B %d, %Y"


class CalendarEventsForm(forms.Form):
    """
    Allows admins to update calendar events
    """

    after = forms.DateField(required=False)
    before = forms.DateField(required=False)
    delete_events = forms.BooleanField(required=False)

    def save(self, request):
        errors = Counter()
        events, courses = 0, 0
        after = self.cleaned_data["after"]
        before = self.cleaned_data["before"]

        if self.cleaned_data["delete_events"]:
            self.delete(request)

        # Get the course object and filter the query
        Course = apps.get_model(app_label="cohort", model_name="Course")
        queryset = Course.objects.all()

        if after:
            queryset = queryset.filter(start__gte=after)

        if before:
            queryset = queryset.filter(start__lt=before)

        for course in queryset:
            try:
                events += len(course.make_calendar_events())
                courses += 1
            except ValueError as e:
                errors[str(e)] += 1

        # Provide feedback via the messaging framework
        for error, count in errors.most_common():
            messages.warning(request, f"{count} errors: {error}")
        messages.success(request, f"created {events} events in {courses} courses")

    def delete(self, request):
        CalendarEvent = apps.get_model(app_label="cohort", model_name="CalendarEvent")
        result, typeinfo = CalendarEvent.objects.all().delete()
        typeinfo = " & ".join([
            "{} ({})".format(key, val) for key, val in typeinfo.items()
        ])
        messages.warning(request, f"deleted {result} objects: {typeinfo}")


class HolidayForm(forms.Form):
    """
    Allows admins to create holiday events
    """

    no_convert = forms.BooleanField(required=False)
    date = forms.DateField()
    title = forms.CharField()

    def save(self, request):
        day = self.cleaned_data["date"]
        title = self.cleaned_data["title"]

        if not self.cleaned_data["no_convert"]:
            # Find the nearest saturday
            if day.weekday() == 6:
                # Shift Sunday holiday to Saturday
                day -= timedelta(days=1)
            elif day.weekday() == 0:
                # Three day weekends for Monday holidays
                day -= timedelta(days=2)
            elif day.weekday() == 1:
                # Do we really move Tuesday holidays back to Saturday?
                day -= timedelta(days=3)
            elif day.weekday() < 5:
                # Move Wednesday, Thursday, Friday to next Saturday
                day += timedelta(days=(5 - day.weekday() + 7) % 7)
            else:
                # This is a Saturday already
                pass

        # Create the calendar event
        CalendarEvent = apps.get_model(app_label="cohort", model_name="CalendarEvent")

        # Check that the holiday doesn't already exist (no uniqueness constraint)
        q = CalendarEvent.objects.filter(
            is_holiday=True,
            start__year=day.year,
            start__month=day.month,
            start__day=day.day
        )
        if q.exists():
            messages.warning(
                request, f"Holiday already scheduled on {day.strftime(DTFMT)}"
            )
            return

        try:
            CalendarEvent.objects.create(
                summary=title, start=day, end=day, is_holiday=True,
            )
        except Exception as e:
            messages.warning(request, f"Could not create holiday: {e}")
            return

        messages.success(request, f"Created holiday on {day.strftime(DTFMT)}")
