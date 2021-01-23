# faculty.forms
# Forms for managing faculty and assignments
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Jan 23 14:08:49 2021 -0500
#
# Copyright (C) 2021 Georgetown University
# For license information, see LICENSE.txt
#
# ID: forms.py [] benjamin@bengfort.com $

"""
Forms for managing faculty and assignments
"""

##########################################################################
## Imports
##########################################################################

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError

from collections import Counter
from faculty.csv import decode_assignments, parse_assignments


_ASSIGNMENTS_FIELDS = frozenset([
    "Semester", "Cohort", "Last Name", "First Name", "Course ID",
    "Course Title", "Effort (%)", "Hours", "Start Date", "End Date",
])


class UploadScheduleForm(forms.Form):
    """
    Allows staff members to upload a CSV of faculty assignments to add to the schedule.
    """

    assignments = forms.FileField()

    def clean_assignments(self):
        """
        Parse the assignments upload and ensure that it is a valid CSV.
        """
        f = self.cleaned_data["assignments"]

        rows = 0
        try:
            for row in decode_assignments(f):
                rows += 1
                for field in _ASSIGNMENTS_FIELDS:
                    if field not in row:
                        raise ValidationError(f"missing required key {field}")

        except Exception as e:
            raise ValidationError(str(e))

        if rows == 0:
            raise ValidationError("CSV file contains no rows")

        return f

    def save(self, request):
        """
        Parse the assignments in the file, saving and updating as necessary. Feedback
        is provided to the user via the messaging framework on the request.
        """
        n_errors = 0
        created, fetched = Counter(), Counter()

        try:
            reader = decode_assignments(self.cleaned_data["assignments"])
            for obj, was_created in parse_assignments(reader):
                if isinstance(obj, Exception):
                    n_errors += 1
                    messages.add_message(request, messages.WARNING, str(obj))
                    continue

                if was_created:
                    created[obj.__class__.__name__] += 1
                else:
                    fetched[obj.__class__.__name__] += 1
        except Exception as e:
            n_errors += 1
            messages.add_message(
                request, messages.WARNING,
                f"processing ended prematurely: {e}"
            )

        msg = (
            f"created {sum(created.values())} objects "
            f"(fetched {sum(fetched.values())} objects, {n_errors} errors)"
        )
        messages.add_message(request, messages.SUCCESS, msg)


class CalendarEventsForm(forms.Form):
    """
    Allows admins to update calendar events
    """
