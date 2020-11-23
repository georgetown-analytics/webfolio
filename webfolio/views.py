# webfolio.views
# Default application views for the application
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Dec 26 11:14:54 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: views.py [] benjamin@bengfort.com $

"""
Default application views for the application
"""

##########################################################################
## Imports
##########################################################################

import webfolio

from datetime import datetime, date, timedelta
from cohort.managers import scheduled_semesters
from cohort.models import SEMESTER, Cohort, Course, CalendarEvent

from django.db.models import Q
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


##########################################################################
## Views
##########################################################################

class Overview(LoginRequiredMixin, TemplateView):

    template_name = "site/overview.html"

    def get_next_capstone_presentations(self):
        applied = Course.objects.filter(title__startswith="Applied")
        applied = applied.ends_after(date.today()).order_by("end").first()
        if applied:
            return applied.end
        return None

    def get_cohort_progress(self):
        cohort = Cohort.objects.current().first()
        if not cohort:
            return None
        return {
            "pcent": cohort.percent_complete(),
            "cohort": cohort.cohort,
        }

    def scheduled_semesters(self):
        for semester, year in scheduled_semesters()[0:2]:
            courses = Course.objects.non_cohort_courses(semester, year)
            yield f"{SEMESTER[semester]} {year:0.0f}", courses

    def current_cohorts(self):
        return Cohort.objects.order_by("end").ends_after(date.today())[0:3]

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context["page"] = "overview"
        context["next_capstone_presentations"] = self.get_next_capstone_presentations()
        context["num_active_courses"] = Course.objects.current().count()
        context["num_upcoming_courses"] = Course.objects.upcoming().count()
        context["cohort_progress"] = self.get_cohort_progress()
        context["current_cohorts"] = self.current_cohorts()
        context["scheduled_semesters"] = dict(self.scheduled_semesters())
        return context


class SchedulingView(LoginRequiredMixin, TemplateView):

    template_name = "site/scheduling.html"

    def get_years(self):
        """
        Return the year in the get request or return the current year
        """
        # Cache the computation for multiple years requests
        # https://docs.djangoproject.com/en/3.0/ref/class-based-views/#specification
        if not hasattr(self, "_year") or not hasattr(self, "_years"):
            try:
                self._year = int(self.request.GET.get('year', date.today().year))
            except ValueError:
                self._year = date.today().year

            years = frozenset([r[0] for r in Cohort.objects.values_list("start__year")])
            self._years = sorted(list(years))

        return self._year, self._years

    def get_saturdays(self):
        """
        Return all of the Saturdays in the specified year, marked with courses
        """
        year = self.get_years()[0]
        day = date(year, 1, 1)

        # Go to the first Saturday
        day += timedelta(days=(5 - day.weekday() + 7) % 7)

        # Iterate through all Saturdays in the year
        while day.year == year:
            yield day
            day += timedelta(days=7)

    def get_days(self):
        """
        Returns the schedule matrix for the view
        """
        days = list(self.get_saturdays())
        return days

    def get_cohorts(self):
        """
        Returns a data structure that maps cohorts to maps of Saturdays to courses.
        """
        # TODO: how do we add advanced data science/reboot here?
        year = self.get_years()[0]
        table = {}
        cohorts = Cohort.objects.filter(
            Q(start__year=year) | Q(end__year=year)
        ).order_by("start")
        for cohort in cohorts:
            dates = {}
            for course in cohort.courses.all():
                for event in course.calendar_events.all():
                    dates[event.start.date()] = course.title
            table[cohort] = dates
        return table

    def get_holidays(self):
        """
        Returns a dictionary of days that are holidays in the calendar and their names.
        """
        year = self.get_years()[0]
        events = CalendarEvent.objects.filter(
            Q(start__year=year) & Q(is_holiday=True)
        )
        events = events.order_by("start").values_list("start", "summary")
        return {s[0].date(): s[1] for s in events}

    def get_context_data(self, **kwargs):
        context = super(SchedulingView, self).get_context_data(**kwargs)
        context["page"] = "scheduling"
        context["year"], context["years"] = self.get_years()
        context["days"] = self.get_days()
        context["cohorts"] = self.get_cohorts()
        context["holidays"] = self.get_holidays()
        return context


##########################################################################
## API Views
##########################################################################

class HeartbeatViewSet(viewsets.ViewSet):
    """
    Endpoint for heartbeat checking, includes status and version.
    """

    permission_classes = [AllowAny]

    def list(self, request):
        return Response({
            "status": "ok",
            "version": webfolio.get_version(),
            "revision": webfolio.get_revision(short=True),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        })


##########################################################################
## Error Views
##########################################################################

def server_error(request, **kwargs):
    return render(request, template_name='errors/500.html', status=500)


def not_found(request, exception, **kwargs):
    return render(request, template_name='errors/404.html', status=404)


def permission_denied(request, exception, **kwargs):
    return render(request, template_name='errors/403.html', status=403)


def bad_request(request, exception, **kwargs):
    return render(request, template_name='errors/400.html', status=400)
