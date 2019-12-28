# faculty.management.commands.parseassignments
# Parse faculty assignments from a CSV file on local disk.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Dec 27 09:52:10 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: parseassignments.py [] benjamin@bengfort.com $

"""
Parse faculty assignments from a CSV file on local disk.
"""

##########################################################################
## Imports
##########################################################################

from collections import Counter
from django.core.management.base import BaseCommand, CommandError
from faculty.csv import read_assignments, parse_assignments


class Command(BaseCommand):
    help = "Parse faculty assignments from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "assignments", nargs="+", metavar="CSV", help="CSV of faculty assignments"
        )

    def handle(self, *args, **options):
        n_errors = 0
        created, fetched = Counter(), Counter()
        for csv in options["assignments"]:
            try:
                reader = read_assignments(csv)
                for obj, was_created in parse_assignments(reader):
                    if isinstance(obj, Exception):
                        n_errors += 1
                        self.stdout.write(self.style.WARNING(str(obj)))
                        continue

                    if was_created:
                        created[obj.__class__.__name__] += 1
                    else:
                        fetched[obj.__class__.__name__] += 1
            except Exception as e:
                raise CommandError("could not parse {}: {}".format(csv, str(e))) from e

        n_files = len(options["assignments"])
        n_created = sum(created.values())
        n_fetched = sum(fetched.values())
        self.stdout.write(self.style.SUCCESS(
            "created {} objects (fetched {} objects, {} errors) from {} csv files".format(
                n_created, n_fetched, n_errors, n_files
            )
        ))
