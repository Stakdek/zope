#!/bin/bash

# path to python interpreter used to create the environment. virtualenv must
# be installed, see Requirements chapter in README
BASE_PYTHON=/usr/bin/python3.7

# zope release to be installed.

ZOPE_RELEASE="4.2.1"

# external app repository cloned into app folder after installation. optional.
EXTERNAL_ZOPE_DATA=

USER_PASS="admin:admin"

# this creates n wsgi instances
WSGI_INSTANCES=1