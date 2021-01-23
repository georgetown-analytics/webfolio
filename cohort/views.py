# cohort.views
# Cohort app views.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 15:06:39 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: views.py [] benjamin@bengfort.com $

"""
Cohort app views.
"""

##########################################################################
## Imports
##########################################################################

from django.urls import reverse
from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from cohort.models import Cohort, Course, Capstone
from cohort.forms import CalendarEventsForm, HolidayForm


class CohortListView(ListView, LoginRequiredMixin):

    model = Cohort
    context_object_name = "cohorts"

    def get_context_data(self, **kwargs):
        context = super(CohortListView, self).get_context_data(**kwargs)
        context["page"] = "cohort/cohorts"
        return context


class CourseListView(ListView, LoginRequiredMixin):

    model = Course
    context_object_name = "courses"

    def get_queryset(self):
        qs = super(CourseListView, self).get_queryset()
        return qs.order_by("-cohort__cohort", "-end")

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        context["page"] = "cohort/courses"
        return context


class CapstoneListView(ListView, LoginRequiredMixin):

    model = Capstone
    context_object_name = "capstones"

    def get_context_data(self, **kwargs):
        context = super(CapstoneListView, self).get_context_data(**kwargs)
        context["page"] = "cohort/capstones"
        return context


##########################################################################
## Administrative Views
##########################################################################

class CalendarEventsView(UserPassesTestMixin, FormView):

    form_class = CalendarEventsForm
    template_name = "scheduling/calendar_events.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse("calendar_events")

    def form_valid(self, form):
        form.save(self.request)
        return super(CalendarEventsView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CalendarEventsView, self).get_context_data(**kwargs)
        context["page"] = "admin/calendar-events"
        return context


class HolidayView(UserPassesTestMixin, FormView):

    form_class = HolidayForm
    template_name = "scheduling/holiday.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse("holiday")

    def form_valid(self, form):
        form.save(self.request)
        return super(HolidayView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(HolidayView, self).get_context_data(**kwargs)
        context["page"] = "admin/holiday"
        return context
