# Zope

Zope (Z Object Publishing Environment) is an object-oriented, open source,
free web application server written in the Python programming language.
Zope is a platform for the realization of web applications and is very well suited
for the creation of dynamic web presences, as it is basically designed to
separate the content from the design of the website.
This Zope-Repo is basically a Makefile and some bash scripts to build a Zope4
instance from scratch into a python virtualenv.
The Zope4 installation is enriched with many useful Zope Prodcuts such as `PythonScripts` or a postgresql
database adapter.

An intention of this repo is to simplify the zope environment setup and therefore
allow easy environment buildup and teardown.

The created zope environment may be customized using the `settings.sh` file.

## Using of Zope

To start zope, a `make start` is enough.
By default, zope runs on localhost:9081, which can be configured to a different port or IP address. See **Via makefile**.

If a different ip address than localhost is selected, then Zope must be started as `root`.

It is recommended to use Zope as Applicationserver and run e.g. HAProxy, Apache2 or nginx as Webserver.
If Zope runs as Applicationserver and Webserver, HTTPS connections do not work and so the connection is insecure.

# Installation

## Requirements

To compile python modules during installation and to checkout git repositories:
```bash
sudo apt-get install build-essential git
```

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

If the the pip product breaks in compiling and building, this may help you.
This is a module to ensure you can run compiled C functions which is needed to install the Products.
For example on all Ubuntu Server LTS‘ will this happen until you install this module.

```bash
sudo apt-get install libffi-dev
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

# Zope instance setup

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

## Database connector setup

To access your postgresql database from zope it is necessary to create a database
connector object in zope. Log in to your zope manage environment and create a
`Z Psycopg 2 Database Connector` object.

Fill the form to configure your connector, most importantly the database
connection string. After you created the connector you can click on it to
open/close the connection or to change its properties.

Create a simple `Z SQL Method` to test your new adapter, content may be `select now()`
or what comes to your mind. Call the query via the Test tab, it should not crash
and hopefully throw the correct result.

Troubleshooting:
+ Watch the console your zope is running in for useful error messages
+ Make sure your connection string is correct, adapter connection must be opened

When using `perfact-zopeplayback` you can even create the database connector in
your `Data.fs` filesystem repository.

```bash
cd /path/to/repo/__root__/
mkdir My_PSQL_Adapter  # may call it chessecake
cd My_PSQL_Adapter
touch __meta__  # consumed by perfact-zopeplayback to create zope objects
```

Following skeleton may be used to fill the `__meta__` file:

```python
[
    ('autocommit', False),
    ('connection_string', 'your connection string here!'),
    ('encoding', ''),
    ('owner', (['acl_users'], 'Your owner here')),
    ('readonlymode', False),
    ('tilevel', 2),
    ('title', 'Useful title here'),
    ('type', 'Z Psycopg 2 Database Connection'),
    ('zdatetime', 'YES'),
]
```

Then use `perfact-zopeplayback` to push the adapter into the `Data.fs`.

## Example for HAProxy
HAProxy is a free, very fast and reliable solution offering high availability,
load balancing, and proxying for TCP and HTTP-based applications.
It is particularly suited for very high traffic web sites and powers quite a number of the world's most visited ones.
Over the years it has become the de-facto standard opensource load balancer,
is now shipped with most mainstream Linux distributions, and is often deployed by default in cloud platforms.

A config can be like this:

This is a config for normal HTTP connections:
```config

global
    maxconn 50000
    log /dev/log local0
    user haproxy
    group haproxy
    stats socket /run/haproxy/admin.sock user haproxy group haproxy mode 660 level admin
    nbproc 2
    nbthread 4
    cpu-map auto:1/1-4 0-3
    ssl-default-bind-ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
    timeout connect 10s
    timeout client 30s
    timeout server 30s
    log global
    mode http
    option httplog
    maxconn 3000

frontend www-http
    bind 10.0.0.3:80
    default_backend zope

backend zope
    balance roundrobin
    option httpchk HEAD /
    default-server check maxconn 20
    server zope localhost:9081
```


This is a config for HTTPS. You will need a valid certificate for HTTPS.
```config
global
	log /dev/log	local0
	log /dev/log	local1 notice
	chroot /var/lib/haproxy
	stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
	stats timeout 30s
	user haproxy
	group haproxy
	daemon
	maxconn 2048
	tune.ssl.default-dh-param 2048

	# Default SSL material locations
	ca-base /etc/ssl/certs
	crt-base /etc/ssl/private

	# Default ciphers to use on SSL-enabled listening sockets.
	ssl-default-bind-ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:RSA+AESGCM:RSA+AES:!aNULL:!MD5:!DSS
	ssl-default-bind-options no-sslv3

defaults
	log	global
	mode	http
	option	httplog
	option	dontlognull
	option forwardfor
	option http-server-close
        timeout connect 5000
        timeout client  50000
        timeout server  50000
	errorfile 400 /etc/haproxy/errors/400.http
	errorfile 403 /etc/haproxy/errors/403.http
	errorfile 408 /etc/haproxy/errors/408.http
	errorfile 500 /etc/haproxy/errors/500.http
	errorfile 502 /etc/haproxy/errors/502.http
	errorfile 503 /etc/haproxy/errors/503.http
	errorfile 504 /etc/haproxy/errors/504.http

frontend www-http
   bind *:80
   reqadd X-Forwarded-Proto:\ http
   default_backend zope

frontend www-https
   bind *:443 ssl crt /etc/haproxy/certs/mysite.de.pem
   reqadd X-Forwarded-Proto:\ https
   acl letsencrypt-acl path_beg /.well-known/acme-challenge/
   use_backend letsencrypt-backend if letsencrypt-acl
   default_backend zope

backend zope
   redirect scheme https if !{ ssl_fc }
   server www-1 localhost:8080 check # Zope Applicationserver

backend letsencrypt-backend
   server letsencrypt 127.0.0.1:54321
```
Read more at [https://www.haproxy.com/de/blog/the-four-essential-sections-of-an-haproxy-configuration/](https://www.haproxy.com/de/blog/the-four-essential-sections-of-an-haproxy-configuration/)
