#!/bin/bash
cd app/
. ./bin/activate
runwsgi instance/etc/zope.ini
