# Zope HomeApp
Zope HomeApp

# ISSUES


# TODO
* Pythonize the installers! Either via args or via input via Terminal
* Autoconfigure!


# Installation WIP

## Requirements

Postgresql 10, default on Ubuntu 18.04:

```bash
sudo apt-get install postgresql postgresql-server-dev-10
```

Depending on your system python3 package availability may vary:

Python3.7:

```bash
sudo apt-get install zope.deprecation python3-dev python3.7-dev python3.7 python3.7-venv
```

Python3.5:

```bash
sudo apt-get install zope.deprecation python3-dev python3.5-dev python3.5 python3.5-venv
```

## Via makefile

* `make install`
* configure in `instance/etc/wsgi.conf` the real instance path like `…/zope/instance`
* configure in `instance/etc/zope.ini` the real ip-address like `host = <IP>`
* If necessary exchange the `zope/instance/var/` folder with yours.
* `make start` → start serving. It will print the URL.

### settings.sh

This file is sourced when installation starts. Its variables are consumed in `install.sh`.
It allows some settings like which python interpreter is used to start from.
