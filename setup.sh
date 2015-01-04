#!/bin/bash

## initialize markerminer webapp environment
## use command line params
if [ "$#" -ne 3 ]; then
    echo ""
    echo "## ----------------------------------------------------------------------"
    echo "[usage]"
    echo "  $0 WWW_DIR HTTPD_DIR PUBLIC_IP_ADDRESS"
    echo "[required]"
    echo "  WWW_DIR: webapp installation directory, normally /var/www/markeminer"
    echo "  HTTPD_DIR: path to httpd directory, normally /etc/httpd"
    echo "  PUBLIC_IP_ADDRESS: public IP address of current machine"
    echo "## ----------------------------------------------------------------------"
    exit
fi

WEB_INSTALL_DIR=$1
HTTPD_DIR=$2
PUBLIC_IP_ADDRESS=$3

## set up virtualhost configuration
sed -e "s:__WEB_INSTALL_DIR__:$WEB_INSTALL_DIR:g" \
    -e "s:__PUBLIC_IP_ADDRESS__:$PUBLIC_IP_ADDRESS:g" \
    contrib/httpd/conf.d/markerminer.conf \
    > $HTTPD_DIR/conf.d/markerminer.conf
