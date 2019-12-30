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

from datetime import datetime, date
from cohort.models import Cohort, Course

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

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context["page"] = "overview"
        context["next_capstone_presentations"] = self.get_next_capstone_presentations()
        context["num_active_courses"] = Course.objects.current().count()
        context["num_upcomming_courses"] = Course.objects.upcomming().count()
        context["cohort_progress"] = self.get_cohort_progress()
        context["current_cohorts"] = Cohort.objects.order_by("end").ends_after(date.today())[0:3]
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
