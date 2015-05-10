## markerminer-webapp
---
MarkerMiner is an easy-to-use, fully automated, open-access bioinformatic
[workflow](https://bitbucket.org/srikarchamala/markerminer) and
[web application](https://bitbucket.org/vivekkrish/markerminer-webapp) for
effective discovery of SCN loci in flowering plants angiosperms
(flowering plants), from user-provided angiosperm transcriptome
assemblies (e.g. <a href="http://onekp.com" target="_blank">OneKP
transcriptome assemblies</a>). It can be run locally or via the web,
and its tabular and alignment outputs facilitate efficient downstream
assessments of phylogenetic utility, locus selection, intron-exon boundary
prediction, and primer or probe development.

View the user manual [here](https://bitbucket.org/srikarchamala/markerminer).

Please refer to [INSTALL](https://bitbucket.org/vivekkrish/markerminer-webapp/src/HEAD/INSTALL?at=master) for detailed instructions.

### Dependencies

* Python (>= 2.7)
    * Modules: Please refer to pip [requirements.txt](https://bitbucket.org/vivekkrish/markerminer-webapp/src/HEAD/requirements.txt?at=master) for list of required modules
* Apache httpd (http://httpd.apache.org)
* Apache mod_wsgi module (https://code.google.com/p/modwsgi/)

### Usage
---
```
## Clone the repository locally
$ git clone --recursive https://bitbucket.org/vivekkrish/markerminer-webapp
$ cd markerminer-webapp

## Edit the site.cfg and set the UPLOADS_DIRECTORY
## This directory is used by the webapp to store and process uploaded transcript files

## Install required python dependencies
$ pip install -r requirements.txt

## Run the following command to start MarkerMiner webapp
## This initiates a live reloading service, serving the webapp
## This server also listens for code changes and appropriately auto-reloads the application
## To stop the server, hit Control + C

$ python markerminer.py
 * Running on http://0.0.0.0:5000/
 * Restarting with reloader

### To deploy webapp in production mode, run the ./setup.sh script
```
