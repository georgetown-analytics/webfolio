# cohort.management.commands.holiday
# Create holidays from the command line.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Mar 21 11:01:39 2020 -0400
#
# Copyright (C) 2020 Georgetown University
# For license information, see LICENSE.txt
#
# ID: holiday.py [] benjamin@bengfort.com $

"""
Create holidays from the command line.
"""

##########################################################################
## Imports
##########################################################################

import pytz

from django.apps import apps
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError


DTFMT = "%A, %B %d, %Y"
TZ = pytz.timezone("America/New_York")


def date(s):
    d = datetime.strptime(s, "%Y-%m-%d")
    return TZ.localize(d)


class Command(BaseCommand):

    help = "create an academic holiday event for the closest Saturday"

    def add_arguments(self, parser):
        parser.add_argument(
            "-C", "--no-convert", action="store_true",
            help="don't convert to nearest saturday"
        )
        parser.add_argument(
            "date", nargs=1, metavar="YYYY-MM-DD",
            type=date, help="date of the holiday"
        )
        parser.add_argument(
            "title", nargs="+", help="the title of the academic holiday"
        )

    def handle(self, *args, **options):
        day = options["date"][0]
        title = " ".join(options["title"])

        if not options["no_convert"]:
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
                day += timedelta(days=(5-day.weekday() + 7) % 7)
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
            self.stdout.write(self.style.ERROR(
                "Holiday already scheduled on {}".format(day.strftime(DTFMT))
            ))
            return

        try:
            CalendarEvent.objects.create(
                summary=title, start=day, end=day, is_holiday=True,
            )
        except Exception as e:
            raise CommandError("could not create holiday: {}".format(e))

        self.stdout.write(self.style.SUCCESS(
            "created holiday on {}".format(day.strftime(DTFMT))
        ))

