#!/bin/sh
## Initialization script to set up the apache environment

if [[ `grep -cP "markerminer" /etc/httpd/conf/httpd.conf` == 0 ]]; then
	PUBLIC_IP_ADDRESS=`dig +short myip.opendns.com @resolver1.opendns.com`
	cp -pr /etc/httpd/conf/httpd.conf{,.orig}
	cat /etc/httpd/conf/httpd.conf.orig /var/www/markerminer/contrib/httpd/vhost.conf | sed -e "s/<____PUBLIC_IP_ADDRESS____>/$PUBLIC_IP_ADDRESS/g" > /etc/httpd/conf/httpd.conf
fi

/etc/init.d/httpd restart
