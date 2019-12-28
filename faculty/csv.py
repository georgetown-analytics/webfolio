# faculty.csv
# Handles interactions between the database and CSV files for Excel support.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Dec 27 07:59:19 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: csv.py [] benjamin@bengfort.com $

"""
Handles interactions between the database and CSV files for Excel support.
"""

##########################################################################
## Imports
##########################################################################

import csv

from django.apps import apps
from datetime import datetime
from itertools import groupby
from operator import itemgetter


def read_assignments(path):
    """
    Read the faculty assignments spreadsheet with expected fields:

        Semester,Cohort,Last Name,First Name,Course ID,Course Title,
        Effort (%),Hours,Start Date,End Date
    """
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {
                key: value.strip() for key, value in row.items()
            }


def parse_assignments(cohort_rows):
    """
    Groups the rows by the Cohort field and parses all information from the cohort.
    Yields tuples of all objects that are fetched or created from the database, along
    with a bool indicating if they were created or not.
    """
    for cohort, assignment_rows in groupby(cohort_rows, itemgetter("Cohort")):
        # materialize all the rows from the iterator
        assignment_rows = list(assignment_rows)

        # Get or create the cohort by cohort number and semester
        Cohort = apps.get_model(app_label="cohort", model_name="Cohort")
        cohort, created = Cohort.objects.get_or_create(
            cohort=int(cohort),
            semester=assignment_rows[0]["Semester"].split()[0][:2].upper(),
            start=find_course_date(assignment_rows, "Foundations", "Start Date"),
            end=find_course_date(assignment_rows, "Applied", "End Date"),
        )
        yield cohort, created

        for course_id, rows in groupby(assignment_rows, itemgetter("Course ID")):
            # materialize all the rows from the iterator
            rows = list(rows)
            is_course = not ((not course_id) or (course_id == "--"))

            if is_course:
                # Combine all of the rows into a single course
                course, created = parse_course(rows, cohort)
                yield course, created

            # Create all faculty assignments from the rows
            for row in rows:
                # Get the faculty member(s)
                try:
                    faculty, created = parse_faculty(row)
                    yield faculty, created
                except ValueError as e:
                    yield ValueError(
                        "no faculty member for {} ({}): could not create assignment".format(
                            row["Course Title"], row["Semester"],
                        )
                    ), False
                    continue

                # Check if this is an assignment or a course
                if is_course:
                    # This is a course so add faculty assignment
                    yield parse_instructor(row, faculty, course)
                else:
                    # This is an assignment
                    yield parse_advisor(row, cohort, faculty)


def parse_faculty(row):
    """
    Parse a faculty member by their name in the row, performs a get_or_create based on
    the first and last name of the faculty member, which isn't ideal but works well.
    """
    kwargs = {
        field.replace(" ", "_").lower(): row[field]
        for field in ("First Name", "Last Name")
        if field in row and row[field] and row[field] != "--"
    }

    if len(kwargs) != 2:
        raise ValueError("row does not contain either first or last name!")

    Faculty = apps.get_model(app_label="faculty", model_name="Faculty")
    return Faculty.objects.get_or_create(**kwargs)


def parse_course(rows, cohort):
    """
    Parse a course instance by the data in the row, returning a get_or_create using the
    cohort number, course ID, title, hours, and start and end date. Note that the cohort
    must be created before parse_course can work.
    """
    kwargs = {
        "cohort": cohort,
    }

    for field, kw in (("Course ID", "course_id"), ("Course Title", "title")):
        values = set(filter(None, [row.get(field, "") for row in rows]))
        if len(values) == 0:
            raise ValueError("missing required field '{}'".format(field))
        elif len(values) > 1:
            raise ValueError("rows do not describe the same course (duplicate ID and title)")
        else:
            kwargs[kw] = values.pop()

    # parse the course id and the section from the course id field
    kwargs["course_id"], kwargs["section"] = kwargs["course_id"].rsplit("-", 1)
    kwargs["section"] = int(kwargs["section"])

    # parse the total number of hourse from all rows in the course
    hours = sum([int(row["Hours"]) if row["Hours"] else 0 for row in rows])
    kwargs["hours"] = hours if hours > 0 else None

    # set the start date as the earliest start date
    kwargs["start"] = parse_dates(rows, "Start Date", min)

    # set the end date as the latest end date
    kwargs["end"] = parse_dates(rows, "End Date", max)

    Course = apps.get_model(app_label="cohort", model_name="Course")
    return Course.objects.get_or_create(**kwargs)


def parse_instructor(row, faculty, course):
    """
    Get or create an instructor assignment from the faculty and the course information.
    """
    kwargs = {
        "course": course,
        "faculty": faculty,
        "effort": int(row["Effort (%)"]) if row["Effort (%)"] else None,
        "primary": True,
    }

    Instructor = apps.get_model(app_label="faculty", model_name="Instructor")
    return Instructor.objects.get_or_create(**kwargs)


def parse_advisor(row, cohort, faculty):
    """
    Get or create an advisor assignment from the cohort, faculty, and row information.
    """
    role = {
        "teaching assistant": "TA",
        "capstone advisor": "CA",
        "faculty advisor": "FD",
        "faculty director": "FD",
    }[row["Course Title"].lower()]

    kwargs = {
        "cohort": cohort,
        "faculty": faculty,
        "role": role,
        "hours": int(row["Hours"]) if row["Hours"] else None,
        "effort": int(row["Effort (%)"]) if row["Effort (%)"] else None,
        "primary": True,
    }

    Advisor = apps.get_model(app_label="faculty", model_name="Advisor")
    return Advisor.objects.get_or_create(**kwargs)


def parse_date(row, field, allow_null=True):
    """
    Parse a date from a csv row, returns None if allow_null is True otherwise raises
    a ValueError if the date isn't available on the row.
    """
    if not row[field]:
        if allow_null:
            return None
        raise ValueError("no date to parse in '{}'".format(field))
    return datetime.strptime(row[field], "%Y-%m-%d").date()


def parse_dates(rows, field, agg=min, allow_null=True):
    """
    Parse date from many csv rows (see parse_date), selecting the date by the specified
    agg function (usually either min or max).
    """
    dates = set(filter(None, [parse_date(row, field, True) for row in rows]))
    if len(dates) == 0:
        if allow_null:
            return None
        raise ValueError("no date to parse in '{}'".format(field))
    return agg(dates)


def find_course_date(rows, course_prefix, field="Start Date", allow_null=True):
    for row in rows:
        if row["Course Title"].startswith(course_prefix):
            return parse_date(row, field, allow_null)
    raise ValueError("could not find course with prefix '{}'".format(course_prefix))
