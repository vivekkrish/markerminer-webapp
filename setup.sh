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

## Clone webapp repository into web accessible directory
git clone --recursive https://bitbucket.org/vivekkrish/markerminer-webapp.git $WEB_INSTALL_DIR
cd $WEB_INSTALL_DIR

## Install dependencies using pip
pip install -r requirements.txt

## Install mod_wsgi (against python2.7)
cd ~/ && mkdir Downloads && cd Downloads
wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.4.8.tar.gz
tar -zxf 4.4.8.tar.gz
cd mod_wsgi-4.4.8/
./configure --with-apxs=/usr/sbin/apxs --with-python=/usr/local/bin/python
make
make install

## Load WSGI module
cp -pr contrib/httpd/conf.d/wsgi.conf /etc/httpd/conf.d/.

## Set up virtualhost configuration
sed -e "s:__WEB_INSTALL_DIR__:$WEB_INSTALL_DIR:g" \
    -e "s:__PUBLIC_IP_ADDRESS__:$PUBLIC_IP_ADDRESS:g" \
    contrib/httpd/conf.d/markerminer.conf \
    > $HTTPD_DIR/conf.d/markerminer.conf

## Update httpd sysconfig script
cp -pr /etc/sysconfig/httpd{,.orig}
cat contrib/sysconfig/httpd >> /etc/sysconfig/httpd

## Restart apache
service httpd graceful


