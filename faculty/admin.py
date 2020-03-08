# faculty.admin
# Faculty app admin site management.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 16:06:48 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: admin.py [] benjamin@bengfort.com $

"""
Faculty app admin site management.
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from .models import Faculty, Assignment, Contact


##########################################################################
## Register your models here
##########################################################################

admin.site.register(Faculty)
admin.site.register(Assignment)
admin.site.register(Contact)
