#!/bin/bash

## initialize markerminer environment
WEB_INSTALL_DIR=/var/www/markerminer
MARKERMINER_REPO="https://bitbucket.org/vivekkrish/markerminer-webapp.git"
HTTPD_DIR=/etc/httpd
PUBLIC_IP_ADDRESS=`dig +short myip.opendns.com @resolver1.opendns.com`

## clone repo if not exists
if [ ! -d "$MARKERMINER_DIR" ]; then
    git clone --recursive $MARKERMINER_REPO $WEB_INSTALL_DIR
else
    git pull
fi

## set up virtualhost config
cd $WEB_INSTALL_DIR
sed -e "s:__WEB_INSTALL_DIR__:$WEB_INSTALL_DIR:g" \
    -e "s:__PUBLIC_IP_ADDRESS__:$PUBLIC_IP_ADDRESS:g" \
    contrib/httpd/conf.d/markerminer.conf \
    > $HTTPD_DIR/conf.d/markerminer.conf

## restart httpd
service httpd graceful
