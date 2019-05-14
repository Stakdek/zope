# Zope HomeApp

Zope HomeApp is basically a Makefile and some bash scripts to build a Zope4
instance from scratch into a python virtualenv. The Zope4 installation is
enriched with many useful Zope Prodcuts such as `PythonScripts` or a postgresql
database adapter.

An intention of this repo is to simplify the zope environment setup and therefore
allow easy environment buildup and teardown.

The created zope environment may be customized using the `settings.sh` file.

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
See comments in `settings.sh` for further detaills.

## Allow custom modules in Products.PythonScripts

The following steps describe how to setup the `PythonScripts` product to allow
arbitrary python modules in zope python scripts.

First create a new python module inside the Prodcuts folder:

```bash
cd app/lib/python3.7/site-packages/Products/   # this is the products folder! not very easy to find
mkdir GlobalModules                            # you may call it cheesecake as well
touch GlobalModules/__init__.py
```

This new "product" is a dummy serving as hook to call stuff from PythonScripts product.

Insert the following into the `__init__.py` for testing purposes:

```python
# Global module assertions for Python scripts
from Products.PythonScripts.Utility import allow_module

allow_module('json')
```

Test Script in zope:

```python
import json

return 'Awesome!'
```

Negative test:

```python
import re

return 'will not work'
```

**Attention!**
Only allow packages you really need, avoid using too many fancy python packages
in zope python sripts. Better write a short wrapper module providing the stuff
you need, keep such magic away from the `Data.fs` !

## zodbsync usage

Zope environments installed using this repo also ship with a handy tool named
`zodbsync`. After the installation you can use it create a filesystem representation
of the `Data.fs` which can be read using `perfact-zoperecord` and written via
`perfact-zopeplayback`.

**Stop your running zope instance,** then setup `zodbsync_config.py`, most importantly:

```python
# Path of the Zope instance configuration to use to
wsgi_conf_path = '/path/to/this/repo/app/instance/etc/wsgi.conf'

# Path to Data.fs which is needed for lookup of object IDs from transaction IDs
# with perfact-zoperecord --watch
datafs_path = '/path/to/this/repo/app/instance/var/Data.fs'

# Base directory of the repository
base_dir = '/place/to/keep/such/repos'
```

Then activate the zope environment and call `perfact-zoperecord` using the altered
configuration file:

```bash
cd /path/to/this/repo/app
. bin/activate
perfact-zoperecord -c ../zodbsync_config.py
```

This will read the `Data.fs` of your zope instance and throw its content to the
`base_dir` folder previously configured.

Now you can alter the files created in the `base_dir` folder, use `perfact-zopeplayback`
to push files back into the `Data.fs`:

```bash
cd /path/to/this/repo/app
. bin/activate
cd /place/to/keep/such/repos   # base_dir !
perfact-zopeplayback -c /path/to/this/repo/zodbsync_config.py /
```

For a more sophisticated usage use the `-h` argument to display further help on
these tools. For even more infos on them visit [the git repo](https://github.com/perfact/zodbsync)


# TODO
* Pythonize the installers! Either via args or via input via Terminal
* Autoconfigure!
