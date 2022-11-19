# webfolio
# The base directory for project related files and the uwsgi controller.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 26 09:27:55 2019 -0600
#
# Copyright (C) 2019 Georgetown University
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
The base directory for project related files and the uwsgi controller.
"""

##########################################################################
## Imports
##########################################################################

from .version import get_version, get_revision, __version_info__

__version__ = get_version()
