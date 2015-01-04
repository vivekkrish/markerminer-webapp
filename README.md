## markerminer-webapp
---
MarkerMiner is a bioinformatic workflow and [webapp](https://bitbucket.org/vivekkrish/markerminer-webapp) that was designed to identify putatively orthologous single-copy nuclear loci present in two or more user-provided angiosperm transcriptome assemblies (e.g. [OneKP](http://onekp.com) transcriptome assemblies). MarkerMiner outputs detailed tabular results and sequence alignments for downstream assessments of phylogenetic utility, locus selection and intron-exon boundary prediction, and primer or probe development for targeted sequencing (see Godden and Jordon-Thaden et al. 2012).

View the user manual [here](http://goo.gl/WmhJFL).

### Installation
---
Follow the steps outlined below to set up a web accessible area to deploy the webapp:

```
## Clone webapp repository into web accessible directory
git clone --recursive http://bitbucket.org/vivekkrish/markerminer-webapp.git /var/www/markerminer
cd /var/www/markerminer

## Install dependencies using pip
pip install -r requirements.txt

## Retrieve the public IP address of your machine
dig +short myip.opendns.com @resolver1.opendns.com

## Run the setup script
./setup.sh /var/www/markerminer /path/to/httpd xxx.xxx.xxx.xxx

## Update httpd sysconfig script
cp -pr /etc/sysconfig/httpd{,.orig}
cat contrib/sysconfig/httpd >> /etc/sysconfig/httpd

## Restart apache
service httpd graceful

## Once apache is restarted, navigate to web-browser and 
## type in the IP address of the machine to access the webapp
```
