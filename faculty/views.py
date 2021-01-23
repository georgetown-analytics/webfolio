# faculty.views
# Faculty app views.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 16:06:48 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: views.py [] benjamin@bengfort.com $

"""
Faculty app views.
"""

##########################################################################
## Imports
##########################################################################

from django.urls import reverse
from django.db import connection
from django.views.generic import FormView
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from faculty.models import Faculty, Assignment, Contact
from faculty.forms import UploadScheduleForm, CalendarEventsForm


class FacultyListView(ListView, LoginRequiredMixin):

    model = Faculty
    context_object_name = "faculty"

    def get_context_data(self, **kwargs):
        context = super(FacultyListView, self).get_context_data(**kwargs)
        context["page"] = "faculty/faculty"
        return context


class FacultyDetailView(DetailView, LoginRequiredMixin):

    model = Faculty
    context_object_name = "faculty"

    def get_context_data(self, **kwargs):
        context = super(FacultyDetailView, self).get_context_data(**kwargs)
        context["page"] = "faculty/faculty"
        return context


class UnassociatedFacultyView(TemplateView, LoginRequiredMixin):

    template_name = "faculty/unassociated.html"

    def get_context_data(self, **kwargs):
        context = super(UnassociatedFacultyView, self).get_context_data(**kwargs)
        context["page"] = "faculty/faculty"
        return context


class AssignmentListView(ListView, LoginRequiredMixin):

    model = Assignment
    template_name = "faculty/assignments_list.html"
    context_object_name = "assignments"

    def get_context_data(self, **kwargs):
        context = super(AssignmentListView, self).get_context_data(**kwargs)
        context["page"] = "faculty/assignments"
        return context


class ContactsListView(ListView, LoginRequiredMixin):

    model = Contact
    template_name = "faculty/contact_list.html"
    context_object_name = "contacts"

    def get_active_faculty(self):
        query = (
            "SELECT f.first_name, f.last_name, f.email, count(a.id) AS assignments "
            "  FROM faculty f "
            "  JOIN assignments a ON a.faculty_id = f.id "
            "  JOIN cohorts c ON a.cohort_id = c.id "
            "WHERE c.start <= NOW()::date and c.end >= NOW()::date "
            "GROUP BY (f.first_name, f.last_name, f.email) "
            "ORDER BY f.last_name "
        )
        results = []
        with connection.cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                name = "{} {}".format(row[0], row[1])
                email = row[2]
                results.append({
                    "name": name, "email": email,
                    "full_email": "{} <{}>".format(name, email),
                    "assignments": int(row[3]),
                })

        return results

    def get_context_data(self, **kwargs):
        context = super(ContactsListView, self).get_context_data(**kwargs)
        context["page"] = "contacts"
        context["faculty"] = self.get_active_faculty()
        context["mailto_all_faculty"] = ", ".join([
            row["full_email"] for row in context["faculty"] if row["email"]]
        )
        return context


##########################################################################
## Administrative Views
##########################################################################

class UploadScheduleView(UserPassesTestMixin, FormView):

    form_class = UploadScheduleForm
    template_name = "faculty/upload_schedule.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse("upload_schedule")

    def form_valid(self, form):
        """
        Parse the uploaded file and create assignments as necessary.
        """
        form.save(self.request)
        return super(UploadScheduleView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UploadScheduleView, self).get_context_data(**kwargs)
        context["page"] = "admin/upload-schedule"
        return context


class CalendarEventsView(UserPassesTestMixin, FormView):

    form_class = CalendarEventsForm
    template_name = "faculty/calendar_events.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse("scheduling")

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, "Hello World!")
        return super(CalendarEventsView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CalendarEventsView, self).get_context_data(**kwargs)
        context["page"] = "admin/calendar-events"
        return context
