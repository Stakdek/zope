# Zope HomeApp
Zope HomeApp

# ISSUES
1. Got an error in startup of Zope4. 
1. Errors in Products.ZPsycopgDA and Products.SimpleUserFolder in startup
1. sometimes errors in installation

# TODO
Pythonize the installers!
Either via args or via input via Terminal 

# Installation WIP
* `make install`
* configure in `instance/etc/wsgi.conf` the real instance path like `…/zope/instance`
* configure in `instance/etc/zope.ini` the real ip-address like `host = <IP>`
* If necessary exchange the `zope/instance/var/` folder with yours.
* `make start` → start serving. It will print the URL.
