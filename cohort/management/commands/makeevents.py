# cohort.management.commands.makeevents
# Make calendar events for a course (or delete courses and remake)
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Mar 16 17:30:05 2020 -0400
#
# Copyright (C) 2020 Georgetown University
# For license information, see LICENSE.txt
#
# ID: makeevents.py [] benjamin@bengfort.com $

"""
Make calendar events for a course (or delete courses and remake)
"""

##########################################################################
## Imports
##########################################################################

from django.apps import apps
from collections import Counter
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = "create all calendar events for all courses"

    def add_arguments(self, parser):
        parser.add_argument(
            "-D", "--delete", action="store_true", help="delete all events before creating them"
        )

    def handle(self, *args, **options):
        errors = Counter()
        events, courses = 0, 0

        if options["delete"]:
            self.delete_all_events()

        Course = apps.get_model(app_label="cohort", model_name="Course")
        for course in Course.objects.all():
            try:
                events += len(course.make_calendar_events())
                courses += 1
            except ValueError as e:
                errors[str(e)] += 1

        for error, count in errors.most_common():
            self.stdout.write(self.style.WARNING("{} errors: {}".format(count, error)))

        self.stdout.write(self.style.SUCCESS(
            "created {} events in {} courses".format(events, courses)
        ))

    def delete_all_events(self):
        CalendarEvent = apps.get_model(app_label="cohort", model_name="CalendarEvent")
        result, typeinfo = CalendarEvent.objects.all().delete()
        typeinfo = "\n  ".join(["{}: {}".format(key, val) for key, val in typeinfo.items()])
        self.stdout.write(self.style.WARNING(
            "deleted {} objects:\n  {}".format(result, typeinfo)
        ))
