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

from webfolio.views import HeartbeatViewSet, Overview


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
    path("admin/", admin.site.urls),

     # Authentication URLs
    path("", include("django.contrib.auth.urls")),
    path("", include(("social_django.urls", "social_django"), namespace="social")),

    # Application URLs
    path("", Overview.as_view(), name="overview"),

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
