#!/bin/bash
set -e

source settings.sh

echo "Create virtualenv"
$BASE_PYTHON -m venv app
cd app
. ./bin/activate
bin/pip install -U pip
bin/pip install wheel

echo "Unpack customized Zope products"
tar -xzvf ../custom-products.tar.gz

if [[ ! -d Zope-$ZOPE_RELEASE ]]; then
    echo "Download and unpack Zope-$ZOPE_RELEASE"
    wget https://github.com/zopefoundation/Zope/archive/$ZOPE_RELEASE.tar.gz
    tar -xzvf $ZOPE_RELEASE.tar.gz
fi

echo "Install Zope4 requirements"
bin/pip install -r Zope-$ZOPE_RELEASE/requirements-full.txt || sudo apt-get install python3-dev && bin/pip install -r Zope-$ZOPE_RELEASE/requirements-full.txt

echo "Install Products"
bin/pip install Products.PythonScripts \
    Products.ZSQLMethods \
    Products.SiteErrorLog \
    Products.StandardCacheManagers \
    Products.ExternalMethod \
    Products.MailHost \
    psycopg2-binary \
    zope.mkzeoinstance

echo "Install Products.PythonScripts"
bin/pip install custom-products/Products.PythonScripts

echo "Install Products.ZSQLMethods"
bin/pip install custom-products/Products.ZSQLMethods

echo "Installed Products.SiteErrorLog"
bin/pip install custom-products/Products.SiteErrorLog/

echo "Install Products.StandardCacheManagers"
bin/pip install Products.StandardCacheManagers

echo "Install Products.ExternalMethod"
bin/pip install Products.ExternalMethod

echo "Install Products.MailHost"
bin/pip install "Products.MailHost[genericsetup]"

echo "Install psycopg2"
bin/pip install psycopg2

echo "Install zope.mkzeoinstance"
bin/pip install zope.mkzeoinstance

echo "Install ZPsycopgDA"
bin/pip install git+https://github.com/perfact/ZPsycopgDA

echo "Install SimpleUserFolder"
bin/pip install git+https://github.com/perfact/SimpleUserFolder

echo "Install PerFact zodbsync"
bin/pip install git+https://github.com/perfact/zodbsync

echo "Make wsgi instance and user"
bin/mkwsgiinstance -d instance -u $USER_PASS
rm -rf ../custom-products/
cd ..



if [ -z ${EXTERNAL_ZOPE_DATA} ]
then
    echo "No custom Zope-Repo found. Skipping…"
else
    # get the name from the git repo link
    REPO_NAME=$(echo $EXTERNAL_ZOPE_DATA| cut -d'/' -f 5 | cut -d'.' -f 1)

    git clone $EXTERNAL_ZOPE_DATA
    cd $REPO_NAME
    if [[ -d app ]]; then
        echo "Will now install $REPO_NAME to Zope-$ZOPE_RELEASE…"
        cp -r app/ ../
        cd ..
        rm -rf $REPO_NAME/
        echo "Custom Repo installation done."
    else
        echo "ERROR: The Repo $REPO_NAME does not have an directory 'app'."
        echo "This folder excepted to make sure the format of the repo is compatible with this Zope-Repo"
        cd ..
        rm -rf $REPO_NAME/
    fi
fi

echo "now running Zope with bash startup.sh."
bash startup.sh
