#!/usr/bin/env python

import os
import os.path as op
import sys
import subprocess
import time
from os import error
from multiprocessing import cpu_count

from flask import Flask, render_template, request, redirect, \
    send_from_directory, url_for, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets import FileInput as _FileInput

from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, FloatField, SelectField, \
    FieldList, FormField, SubmitField, ValidationError, validators
from wtforms.validators import Required

from flask.ext.mandrill import Mandrill

from filesystem import Folder, File
from action import *


SCRIPT_PATH = op.dirname(op.abspath(__file__))
choices = [(x, "{0}. {1}".format(x[:1], x[1:])) for x in \
    os.listdir(op.join(SCRIPT_PATH, 'pipeline', 'Resources'))]
ALLOWED_EXTENSIONS = ['fa', 'fasta', 'fsa', 'fna', 'txt']
  
  
class FileInput(_FileInput):
    def __init__(self, multiple=False):
        self.multiple = multiple
  
    def __call__(self, field, **kwargs):
        if self.multiple:
            kwargs['multiple'] = 'multiple'
  
        return super(FileInput, self).__call__(field, **kwargs)
  
  
class MultiFileField(FileField):
    widget = FileInput(multiple=True)


class JobSubmitForm(Form):
    fileupload = MultiFileField('Input FASTA file(s)', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS, 'Plain-text FASTA file(s) only!')
    ])

    singleCopyReference = SelectField(u'Select single copy transcript reference', \
        choices=list(choices))

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


def build_transcript_files_list(files, dir):
    filePaths = op.join(dir, "file_paths.txt")
    fw = open(filePaths, "w")
    for filename in files:
        print >> fw, op.join(dir, filename)
    fw.close()

    return filePaths


def build_job_cmd(form, files, upload_dir, results_dir, debug=False):
    filePaths = build_transcript_files_list(files, upload_dir)
    job_cmd = [op.join(SCRIPT_PATH, 'pipeline', \
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
        '-logfileName', 'pipeline_log.out']
    if debug:
        job_cmd.append('-debug')
    return " ".join(str(x) for x in job_cmd)


def upload_files(form, dir):
    mkdir_p(dir)
    files = []
    for data in form.fileupload.raw_data:
        filename = secure_filename(data.filename)
        if filename not in files:
            data.save(op.join(dir, filename))
            files.append(filename)

    return files


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)
    mandrill = Mandrill(app)

    @app.route('/', methods=('GET', 'POST'))
    def index():
        form = JobSubmitForm(singleCopyReference="Athaliana" , minTranscriptLen=900, \
            minProteinCoverage=80, minTranscriptCoverage=70, minSimilarity=70, cpus=3)

        if request.method == 'POST' and form.validate_on_submit(): # to get error messages to the browser
            ts = str(int(time.time()))
            UPLOADS_DIRECTORY = op.join(app.config['UPLOADS_DIRECTORY'], ts)
            RESULTS_DIRECTORY = UPLOADS_DIRECTORY.replace('uploads', 'results')
            files = upload_files(form, UPLOADS_DIRECTORY)
            email = form.email.data
            cmd = build_job_cmd(form, files, UPLOADS_DIRECTORY, RESULTS_DIRECTORY, debug=app.config['DEBUG'])

            return redirect(url_for('submit', cmd=cmd, email=email, result_url=op.join(request.url_root, 'results', ts)))

        return render_template('index.html', form=form)

    @app.route('/help')
    def help():
        return render_template('help.html')

    @app.route('/submit')
    def submit():
        cmd, email, request_url = request.args['cmd'], request.args['email'], request.args['request_url']
        
        subprocess.Popen(cmd.split(" "), shell=False)
        mandrill.send_email(
            to=[{'email': email}],
            text='Thank you for using the MarkerMiner pipeline.\n\n' + 
                 'The following command was submitted:\n\n {0}\n\n'.format(cmd) + 
                 'Your results will be accessible at: {0}'.format(result_url)
        )

        return render_template('submit.html', cmd=cmd, email=email, result_url=result_url)

    @app.route('/results/<path:path>')
    def browser(path=None):
        path_join = os.path.join(app.config['RESULTS_DIRECTORY'], path)
        if os.path.isdir(path_join):
            folder = Folder(app.config['RESULTS_DIRECTORY'], path)
            folder.read()
            return render_template('folder.html', folder=folder)
        else:
            my_file = File(app.config['RESULTS_DIRECTORY'], path)
            context = my_file.apply_action(View)
            folder = Folder(app.config['RESULTS_DIRECTORY'], my_file.get_path())
            if context == None:
                return render_template('file_unreadable.html', folder=folder)
            return render_template('file_view.html', text=context['text'], file=my_file, folder=folder)

    @app.route('/results/download/<path:path>')
    def download(path=''):
        return send_from_directory(app.config['RESULTS_DIRECTORY'], path)

    return app


if __name__ == '__main__':
    create_app(configfile='site.cfg').run(host='0.0.0.0', debug=True)
