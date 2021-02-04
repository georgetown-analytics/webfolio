# cohort.admin
# Cohort app admin site.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 15:06:39 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: admin.py [] benjamin@bengfort.com $

"""
Cohort app admin site.
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from faculty.models import Assignment
from cohort.models import Cohort, Course, Capstone, CalendarEvent


##########################################################################
## Admin Forms
##########################################################################

class AssignmentsInline(admin.StackedInline):

    model = Assignment
    extra = 1


class CourseAdmin(admin.ModelAdmin):

    inlines = [
        AssignmentsInline
    ]


##########################################################################
## Register your models here
##########################################################################

admin.site.register(Cohort)
admin.site.register(Capstone)
admin.site.register(CalendarEvent)
admin.site.register(Course, CourseAdmin)
