# faculty.templatetags.gravatar
# Gravatar helpers for faculty profile images
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Dec 28 15:58:52 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: gravatar.py [] benjamin@bengfort.com $

"""
Gravatar helpers for faculty profile images
"""

##########################################################################
## Imports
##########################################################################

from hashlib import md5
from django import template

register = template.Library()


##########################################################################
## Template Tags
##########################################################################

@register.filter(name='gravatar')
def gravatar(user, size=35):
    if hasattr(user, "faculty") and user.faculty is not None:
        email = user.faculty.get_email()
    else:
        email = user.email

    email = str(user.email.strip().lower()).encode('utf-8')
    email_hash = md5(email).hexdigest()
    url = "//www.gravatar.com/avatar/{0}?s={1}&d=identicon&r=PG"
    return url.format(email_hash, size)
