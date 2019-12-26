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

from django.urls import path
from django.contrib import admin

from django.views.generic import TemplateView


##########################################################################
## URL Patterns
##########################################################################

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),

     # Application URLs
    path('', TemplateView.as_view(template_name="page.html"), name="home"),
]

##########################################################################
## Error handling
##########################################################################

# handler400 = 'webfolio.views.bad_request'
# handler403 = 'webfolio.views.permission_denied'
# handler404 = 'webfolio.views.not_found'
# handler500 = 'webfolio.views.server_error'
