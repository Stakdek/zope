# Zope HomeApp
Zope HomeApp


# Installation
* `make install`
* configure in `instance/etc/wsgi.conf` the real instance path like `…/zope/instance`
* configure in `instance/etc/zope.ini` the real ip-address like `host = <IP>`
* If necessary exchange the `zope/instance/var/` folder with yours.
* `make start` → start serving. It will print the URL.
