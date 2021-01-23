# webfolio.urls
# webfolio URL Configuration
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 09:27:55 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: urls.py [] benjamin@bengfort.com $

"""webfolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from rest_framework import routers
from django.urls import path, include

from faculty.views import UploadScheduleView, CalendarEventsView
from faculty.views import UnassociatedFacultyView, ContactsListView
from webfolio.views import HeartbeatViewSet, Overview, SchedulingView
from cohort.views import CohortListView, CourseListView, CapstoneListView
from faculty.views import FacultyListView, AssignmentListView, FacultyDetailView

##########################################################################
## Endpoint Discovery
##########################################################################

# Top level router
router = routers.DefaultRouter()
router.register(r'status', HeartbeatViewSet, "status")


##########################################################################
## URL Patterns
##########################################################################

urlpatterns = [
    # Admin URLs
    path('grappelli/', include('grappelli.urls')),
    path("admin/", admin.site.urls),

     # Authentication URLs
    path("", include("django.contrib.auth.urls")),
    path("", include(("social_django.urls", "social_django"), namespace="social")),

    # Application URLs
    path("", Overview.as_view(), name="overview"),
    path("scheduling/", SchedulingView.as_view(), name="scheduling"),
    path("cohorts/", CohortListView.as_view(), name="cohort_list"),
    path("courses/", CourseListView.as_view(), name="course_list"),
    path("capstones/", CapstoneListView.as_view(), name="capstone_list"),
    path("contacts/", ContactsListView.as_view(), name="contact_list"),
    path("faculty/", FacultyListView.as_view(), name="faculty_list"),
    path("faculty/assignments/", AssignmentListView.as_view(), name="assignment_list"),
    path("faculty/unassociated/", UnassociatedFacultyView.as_view(), name="faculty_unassociated"),
    path("faculty/<slug:slug>/", FacultyDetailView.as_view(), name="faculty_detail"),
    path("upload/schedule/", UploadScheduleView.as_view(), name="upload_schedule"),
    path("calendar/", CalendarEventsView.as_view(), name="calendar_events"),

    ## REST API Urls
    path('api/', include((router.urls, 'rest_framework'), namespace="api")),
]

##########################################################################
## Error handling
##########################################################################

handler400 = "webfolio.views.bad_request"
handler403 = "webfolio.views.permission_denied"
handler404 = "webfolio.views.not_found"
handler500 = "webfolio.views.server_error"
