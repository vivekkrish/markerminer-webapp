#!/bin/bash

## initialize markerminer environment
MARKERMINER_REPO="https://github.com/vivekkrish/markerminer-webapp.git"
WEB_INSTALL_DIR=/var/www/markerminer
HTTPD_DIR=/etc/httpd
PUBLIC_IP_ADDRESS=`dig +short myip.opendns.com @resolver1.opendns.com`

## change permissions on WEB_INSTALL_DIR
chmod 777 $WEB_INSTALL_DIR

## clone repo if local copy not exists, else
if [ ! -d "$MARKERMINER_DIR" ]; then
    git clone --recursive $MARKERMINER_REPO $WEB_INSTALL_DIR
fi

## if local copy exists, pull remote changes and update pipeline submodule
cd $WEB_INSTALL_DIR
git pull origin master
git submodule update --recursive

## set up virtualhost config
sed -e "s:__WEB_INSTALL_DIR__:$WEB_INSTALL_DIR:g" \
    -e "s:__PUBLIC_IP_ADDRESS__:$PUBLIC_IP_ADDRESS:g" \
    contrib/httpd/conf.d/markerminer.conf \
    > $HTTPD_DIR/conf.d/markerminer.conf

## restart httpd
service httpd graceful
