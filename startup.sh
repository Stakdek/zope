#!/bin/bash
DIR="$(dirname "$(readlink -f "$0")")" # get path of script
echo $DIR
cd $DIR/app/
. ./bin/activate
runwsgi instance$1/etc/zope.ini
