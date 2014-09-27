#!/usr/bin/env python

import os
import os.path as op
import sys
import errno
import shlex
import subprocess
import re
from tempfile import mkdtemp
from os import error
from multiprocessing import cpu_count

from flask import Flask, render_template, request, redirect, \
    send_from_directory, url_for, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import StringField, IntegerField, FloatField, SelectField, \
    FieldList, FormField, SubmitField, ValidationError, validators
from wtforms.widgets import FileInput as _FileInput
from wtforms.validators import Required
from wtforms.compat import string_types

from werkzeug.utils import secure_filename
from flask.ext.mandrill import Mandrill

from filesystem import Folder, File
from action import *


SCRIPT_PATH = op.dirname(op.abspath(__file__))
ALLOWED_EXTENSIONS = ['fa', 'fasta', 'fsa', 'fna', 'txt']
ORGANISMS = []
fp = open(op.join(SCRIPT_PATH, 'pipeline', 'Resources', 'organisms.tsv'), 'r')
for line in fp:
    o = line.split('\t')
    ORGANISMS.append((o[0], o[1]))
fp.close()
ORGANISMS.sort(key=lambda x:x[0], reverse=False)
"""
ORGANISMS = [(x, "{0}. {1}".format(x[:1], x[1:])) for x in \
    os.listdir(op.join(SCRIPT_PATH, 'pipeline', 'Resources'))]
ORGANISMS.sort()
"""
 


class FileInput(_FileInput):
    def __init__(self, multiple=False):
        self.multiple = multiple
  
    def __call__(self, field, **kwargs):
        if self.multiple:
            kwargs['multiple'] = 'multiple'
  
        return super(FileInput, self).__call__(field, **kwargs)
  
  
class MultiFileField(FileField):
    widget = FileInput(multiple=True)


def regexp(regex, flags=0):
    regex = re.compile(regex, flags)

    def _regexp(form, field):
        invalid_files = []
        for data in form.fileupload.raw_data:
            filename = data.filename
            match = regex.match(filename or '')
            if not match:
                invalid_files.append(filename)
                
        if len(invalid_files) > 0:
            message = 'Error: Please check following filename(s): {0}'.format([str(x) for x in invalid_files]) + \
                '. They should be of the form `ABCD-Trans_assembly_1_sample.fa`.'

            raise ValidationError(message)

    return _regexp


class JobSubmitForm(Form):
    fileupload = MultiFileField('Input FASTA file(s). <a href="download_sample_data">Download sample dataset</a>', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS, 'Plain-text FASTA file(s) only!'),
        regexp(u'(?=.*-)[a-zA-Z0-9-]+')
    ])

    singleCopyReference = SelectField(u'Select single copy transcript reference', \
        choices=list(ORGANISMS))

    minTranscriptLen = IntegerField('Minimum transcript length')
    minProteinCoverage = FloatField('Minimum percentage of protein length aligned', \
        [validators.NumberRange(max=100)])
    minTranscriptCoverage = FloatField('Minimum percentage of transcript length aligned', \
        [validators.NumberRange(max=100)])
    minSimilarity = FloatField('Minimum similarity percent with which sequences are aligned', \
        [validators.NumberRange(max=100)])

    cpus = IntegerField('Number of CPUs to use', [validators.NumberRange(min=1, max=cpu_count())])

    email = StringField('Email address (to send notification)', \
    [validators.Email(message='Please provide a valid email address')])

    submit_button = SubmitField('Submit Job')


def mkdir_p(dir):
    try:
        os.makedirs(dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and op.isdir(dir):
            pass
        else: raise


def build_job_cmd(form, filePaths, upload_dir, results_dir, debug=False):
    job_cmd = [sys.executable, \
        op.join(SCRIPT_PATH, 'pipeline', \
        'single_gene_identification.py'), \
        '-transcriptFilePaths', filePaths, \
        '-singleCopyReference', form.singleCopyReference.data, \
        '-minTranscriptLen', form.minTranscriptLen.data, \
        '-minProteinCoverage', form.minProteinCoverage.data, \
        '-minTranscriptCoverage', form.minTranscriptCoverage.data, \
        '-minSimilarity', form.minSimilarity.data, \
        '-cpus', form.cpus.data, \
        '-outputDirPath', results_dir, \
        '-outputFile', 'single_copy_genes.out', \
        '-logfileName', 'pipeline_log.out', \
        '-email', '"{0}"'.format(form.email.data)]
    if debug:
        job_cmd.append('-debug')
    return " ".join(str(x) for x in job_cmd)


def build_transcript_files_list(files, dir):
    filePaths = "{0}.list.txt".format(dir)
    fw = open(filePaths, "w")
    for filename in files:
        print >> fw, op.join(dir, filename)
    fw.close()

    return filePaths


def upload_files(form, dir):
    files = []
    for data in form.fileupload.raw_data:
        filename = secure_filename(data.filename)
        if filename not in files:
            data.save(op.join(dir, filename))
            files.append(filename)

    return build_transcript_files_list(files, dir)


def send_email(mandrill, email, result_url, download_url, cmd, debug=False):
    if debug == False:
        cmd = ''
    subject = 'MarkerMiner pipeline status: Submitted'
    email_text = """
Thank you for using the MarkerMiner pipeline.
{0}

While the job is in progress, intermediate results and logs can be viewed here: {1}

Once the job has run to completion you should receive an email notification.
At this point, the above link will be become inactivated.

List of putative single copy genes and supporting output files 
(in zip format) can be downloaded from here: {2}

If you use MarkerMiner in your research, please cite us:

Chamala, S., Garcia, N., Godden, G.T., Krishnakumar, V., Jordon-Thaden, I. E., 
Barbazuk, W. B., Soltis, D.E., Soltis, P.S. (2014) MarkerMiner 1.0: A new 
bioinformatic workflow and application for phylogenetic marker development 
using angiosperm transcriptomes. Applications in Plant Sciences X: XX-XX
    """.format(cmd, result_url, download_url)

    mandrill.send_email(
        to = [{ 'email' : email }], 
        subject = subject,
        text = email_text,
    )


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)
    mandrill = Mandrill(app)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = JobSubmitForm(singleCopyReference="Athaliana", minTranscriptLen=900, \
            minProteinCoverage=80, minTranscriptCoverage=70, minSimilarity=70, cpus=1)

        if request.method == 'POST' and form.validate_on_submit(): # to get error messages to the browser
            mkdir_p(app.config['UPLOADS_DIRECTORY'])
            UPLOADS_DIRECTORY = mkdtemp(dir=app.config['UPLOADS_DIRECTORY'])
            RESULTS_DIRECTORY = "{0}-output".format(UPLOADS_DIRECTORY)
            debug = app.config['DEBUG']

            filePaths = upload_files(form, UPLOADS_DIRECTORY)
            cmd = build_job_cmd(form, filePaths, UPLOADS_DIRECTORY, RESULTS_DIRECTORY, debug=debug)

            return redirect(
                url_for(
                    'submit', cmd=cmd, email=form.email.data, \
                    result_url=op.join(request.url_root, 'results', \
                        '{0}-output'.format(op.basename(UPLOADS_DIRECTORY))),
                    download_url=op.join(request.url_root, 'results', 'download', \
                        '{0}-output.zip'.format(op.basename(UPLOADS_DIRECTORY)))
                )
            )

        return render_template('index.html', form=form)

    @app.route('/help')
    def help():
        return render_template('help.html')

    @app.route('/submit')
    def submit():
        cmd, email, result_url, download_url = request.args['cmd'], request.args['email'], \
            request.args['result_url'], request.args['download_url']
        
        debug = app.config['DEBUG']

        subprocess.Popen(shlex.split(cmd), env=os.environ)
        send_email(mandrill, email, result_url, download_url, cmd, debug=debug)

        return render_template('submit.html', debug=debug, cmd=cmd, email=email, \
            result_url=result_url, download_url=download_url)

    @app.route('/results/<path:path>')
    def browser(path=None):
        path_join = op.join(app.config['UPLOADS_DIRECTORY'], path)
        if op.isdir(path_join):
            folder = Folder(app.config['UPLOADS_DIRECTORY'], path)
            folder.read()
            return render_template('folder.html', folder=folder)
        else:
            my_file = File(app.config['UPLOADS_DIRECTORY'], path)
            context = my_file.apply_action(View)
            folder = Folder(app.config['UPLOADS_DIRECTORY'], my_file.get_path())
            if context == None:
                return render_template('file_unreadable.html', folder=folder)
            return render_template('file_view.html', text=context['text'], file=my_file, folder=folder)

    @app.route('/results/download/<path:path>')
    def download(path=''):
        return send_from_directory(app.config['UPLOADS_DIRECTORY'], path)

    @app.route('/download_sample_data')
    def sample_data():
        from shutil import make_archive

        sample_data_file = 'Sample_Data'
        sample_data_path = op.join(SCRIPT_PATH, 'pipeline', sample_data_file)
        sample_data_zip_base = op.join(app.config['UPLOADS_DIRECTORY'], sample_data_file)
        make_archive(sample_data_zip_base, format="zip", root_dir=sample_data_path)

        return send_from_directory(app.config['UPLOADS_DIRECTORY'], "{0}.zip".format(sample_data_file))

    return app


if __name__ == '__main__':
    create_app(configfile='site.cfg').run(host='0.0.0.0', debug=True)
