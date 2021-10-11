#!/bin/bash
set -e

source settings.sh

START=startup.sh

sudo rm -f /usr/bin/start_zope
sudo chmod -x $START
sudo chmod 775 $START
sudo ln -s $PWD/$START /usr/bin/start_zope
sudo cp zope@.service /etc/systemd/system
sudo systemctl daemon-reload
if [[ $WSGI_INSTANCES -eq 1 ]];
then
    sudo systemctl enable zope@$WSGI_INSTANCES.service
    sudo systemctl restart zope@$WSGI_INSTANCES.service
else
    sudo systemctl enable zope@{1..$WSGI_INSTANCES}.service
    sudo systemctl restart zope@{1..$WSGI_INSTANCES}.service
fi
exit 0