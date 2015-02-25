## markerminer-webapp
---
MarkerMiner is a bioinformatic [workflow](https://bitbucket.org/srikarchamala/markerminer) and [webapp](https://bitbucket.org/vivekkrish/markerminer-webapp) designed 
to identify putatively orthologous single-copy nuclear loci present in two or more user-provided angiosperm transcriptome 
assemblies (e.g. [OneKP](http://onekp.com) transcriptome assemblies). MarkerMiner outputs detailed tabular results and 
sequence alignments for downstream assessments of phylogenetic utility, locus selection and intron-exon boundary prediction, 
and primer or probe development for targeted sequencing (see Godden and Jordon-Thaden et al. 2012).

View the user manual [here](http://goo.gl/WmhJFL).

Please refer to [INSTALL](https://bitbucket.org/vivekkrish/markerminer-webapp/src/HEAD/INSTALL?at=master) for detailed instructions.

### Dependencies

* Apache httpd
* Apache mod_wsgi module
* Python (>= 2.7)
    * Modules: Please refer to pip [requirements.txt](https://bitbucket.org/vivekkrish/markerminer-webapp/src/HEAD/requirements.txt?at=master) for list of required modules

### Usage
---
```
## Run the following command to start MarkerMiner webapp
## This initiates a live reloading service, serving the webapp
## This server also listens for code changes and appropriately auto-reloads the application
## To stop the server, hit Control + C

$ python markerminer.py
 * Running on http://0.0.0.0:5000/
 * Restarting with reloader

### To deploy webapp in production mode, run the ./setup.sh script
```
