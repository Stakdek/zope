#!/bin/bash
# set -e
sudo apt-get install python3-dev -y
sudo apt-get install python3.5-dev -y
sudo apt-get install python3.5 -y
sudo apt-get install python3.5-venv -y
sudo rm -rf app/
#cd ..
python3.5 -m venv app
cd app
pwd
. ./bin/activate
pwd
bin/pip install -U pip
bin/pip install wheel
# tar -xzvf Zope.tar.gz
tar -xzvf custom-products.tar.gz

if [[ ! -d Zope ]]; then
    echo "Clone Zope4"
    git clone https://github.com/zopefoundation/Zope.git
    ( cd Zope; git checkout 4.0b10 )
fi

echo "Install Zope4 beta requirements"
echo "Install Zope4 requirements"
# REMARK: if this breaks, try installing python3-dev
bin/pip install -r Zope/requirements-full.txt

echo "Install Products"
bin/pip install Products.PythonScripts \
    Products.ZSQLMethods \
    Products.SiteErrorLog \
    Products.StandardCacheManagers \
    Products.ExternalMethod \
    Products.MailHost \
    psycopg2-binary \
    zope.mkzeoinstance
pwd
#cd zope
echo "Install Products.PythonScripts"
bin/pip install custom-products/Products.PythonScripts

echo "Install customized Products.ZSQLMethods"
bin/pip install custom-products/Products.ZSQLMethods

echo "Installed cloned Products.SiteErrorLog"
bin/pip install custom-products/Products.SiteErrorLog/

echo "Install Products.StandardCacheManagers"
bin/pip install Products.StandardCacheManagers

echo "Install Products.ExternalMethod"
bin/pip install Products.ExternalMethod

echo "Install Products.MailHost"
# This should not require to set the option genericsetup. Will hopefully
# not be necessary in some next version
bin/pip install "Products.MailHost[genericsetup]"

echo "Install psycopg2"
bin/pip install psycopg2

echo "Install mkzeoinstance"
bin/pip install zope.mkzeoinstance

echo "Install customized ZPsycopgDA"
bin/pip install -e custom-products/ZPsycopgDA

echo "Install customized SimpleUserFolder"
bin/pip install -e custom-products/SimpleUserFolder

# NOTE: Maybe use -e flag to simplify on-the-fly changes.
echo "Install customized ZPerFactMods"
# bin/pip install -e custom-products/ZPerFactMods

echo "Install customized Products.PerFactErrors"
# bin/pip install -e custom-products/Products.PerFactErrors

echo "Install zodbsync"
# bin/pip install -e custom-products/perfact-zodbsync

echo "Recreating zeo and wsgiinstance"
bin/mkzeoinstance zeo 127.0.0.1:9011
bin/mkwsgiinstance -d instance -u morty:33787951
rm -rf custom-products/
cd ..
cp ./instance/ app/
echo "Done. Run with runzeo and runwsgi"
echo "now running Zope with bash startup.sh"
bash startup.sh
