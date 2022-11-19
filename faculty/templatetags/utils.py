# faculty.templatetags.utils
# Template filters and tags - generic utilties for the entire project.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Dec 30 13:18:22 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: utils.py [] benjamin@bengfort.com $

"""
Template filters and tags - generic utilties for the entire project.
"""

##########################################################################
## Imports
##########################################################################

from django import template

register = template.Library()


##########################################################################
## Template Tags
##########################################################################

@register.filter(name='startswith')
def startswith(text, prefix):
    if isinstance(text, str):
        return text.startswith(prefix)
    return False


@register.filter(name='dget')
def dget(d, key):
    return d.get(key, "")
