# cohort.management.commands.gcal
# Synchronize Google Calendar events
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 10 10:48:41 2021 -0500
#
# Copyright (C) 2020 Georgetown University
# For license information, see LICENSE.txt
#
# ID: gcal.py [] benjamin@bengfort.com $

"""
Synchronize Google Calendar events
"""

##########################################################################
## Imports
##########################################################################

import os.path
import datetime

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ['https://www.googleapis.com/auth/calendar']
ACCOUNT = 'tmp/gcal/credentials.json'
TOKEN = 'tmp/gcal/token.json'


class Command(BaseCommand):

    help = "synchronize google calendar with events"

    def add_arguments(self, parser):
        parser.add_argument(
            "-u", "--user", type=str, required=True,
            help="specify the user to get calendar events for"
        )
        parser.add_argument(
            "-t", "--token", default=TOKEN,
            help="path to token file for user",
        )
        parser.add_argument(
            "-a", "--account", default=ACCOUNT,
            help="path to credentials JSON for API access",
        )
        parser.add_argument(
            "-c", "--calendar", default="primary",
            help="calendar ID to add the events to",
        )

    def handle(self, *args, **options):
        # Get the user to create the events for
        Faculty = apps.get_model(app_label="faculty", model_name="Faculty")
        try:
            person = Faculty.objects.get(netid=options["user"])
        except Faculty.DoesNotExist:
            raise CommandError(f"'{options['user']}' is not a valid netid")

        # Login with Google
        self.login(options.get("token"), options.get("account"))

        # Get the calendar events for the courses and create them
        for course in person.courses.filter(start__gt=datetime.date.today()):
            if course.calendar_events.count() == 0:
                print(f"{course} does not have calendar events")
                continue

            for event in course.calendar_events.all():
                try:
                    e = self.service.events().insert(
                        calendarId=options["calendar"], body=event.json()
                    ).execute()
                    print(f"{event} created: {e.get('htmlLink')}")
                except Exception as e:
                    print(f"could not create {event} - {e}")

    def login(self, token, account):
        # TODO: save token in database of faculty user
        creds = None
        if os.path.exists(token):
            creds = Credentials.from_authorized_user_file(token, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # TODO: store credentials in environment rather than in file
                key = settings.CALENDAR_GOOGLE_OAUTH2_KEY
                secret = settings.CALENDAR_GOOGLE_OAUTH2_SECRET

                if not key or not secret:
                    raise CommandError("no Google credentials to connect to API with")

                flow = InstalledAppFlow.from_client_secrets_file(account, SCOPES)
                creds = flow.run_local_server(port=61947)

                with open(token, 'w') as token:
                    token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)
