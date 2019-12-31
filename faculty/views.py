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

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from faculty.models import Faculty, Assignment


class FacultyListView(ListView, LoginRequiredMixin):

    model = Faculty
    context_object_name = "faculty"

    def get_context_data(self, **kwargs):
        context = super(FacultyListView, self).get_context_data(**kwargs)
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