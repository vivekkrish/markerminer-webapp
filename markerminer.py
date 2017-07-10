#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as op
import shlex
import subprocess

from tempfile import mkdtemp
from multiprocessing import cpu_count

from flask import Flask, render_template, request, redirect, \
    send_from_directory, url_for
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import StringField, IntegerField, FloatField, SelectField, \
    FieldList, FormField, SubmitField, ValidationError, validators
from wtforms.widgets import FileInput as _FileInput
from wtforms.validators import Email, Optional

from sendmail import EmailClient
from helpers import regexp, mkdir_p, upload_files, build_job_cmd, \
    get_result_url, SCRIPT_PATH, ALLOWED_EXTENSIONS, ORGANISMS

from filesystem import Folder, File
from action import View


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
    fileupload = MultiFileField('Input FASTA file(s). <a href="download_sample_data">Download sample dataset</a>', \
        validators=[
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
        validators=[
            Optional(),
            Email(message='Please provide a valid email address')
        ])

    submit_button = SubmitField('Submit Job')


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)
    email_handler = EmailClient(email_from=app.config['EMAIL_DEFAULT_FROM'], \
                                from_name=app.config['EMAIL_FROM_NAME'], \
                                api_key=app.config['EMAIL_API_KEY'])

    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = JobSubmitForm(singleCopyReference="Athaliana", minTranscriptLen=900, \
            minProteinCoverage=80, minTranscriptCoverage=70, minSimilarity=70, cpus=1)

        if request.method == 'POST' and form.validate_on_submit(): # to get error messages to the browser
            mkdir_p(app.config['UPLOADS_DIRECTORY'])
            UPLOADS_DIRECTORY = mkdtemp(dir=app.config['UPLOADS_DIRECTORY'])
            RESULTS_DIRECTORY = "{0}-output".format(UPLOADS_DIRECTORY)
            upload_files(form, UPLOADS_DIRECTORY)
            debug = app.config['DEBUG']

            cmd = build_job_cmd(form, UPLOADS_DIRECTORY, RESULTS_DIRECTORY, debug=debug)
            subprocess.Popen(shlex.split(cmd), env=os.environ)

            job_id = op.basename(UPLOADS_DIRECTORY)
            result_url = get_result_url(request, job_id)
            email_to = form.email.data if form.email.data else ''
            if email_to != '':
                email_handler.send_email(email_to, result_url)

            return redirect(url_for('status', job_id=job_id))

        return render_template('index.html', form=form)

    @app.route('/help')
    def help():
        return render_template('help.html')

    @app.route('/status/<job_id>')
    def status(job_id):
        result_url = get_result_url(request, job_id)

        return render_template('status.html', result_url=result_url)

    @app.route('/results/<path:path>')
    def browser(path=None):
        uploads_dir = app.config['UPLOADS_DIRECTORY']
        path_join = op.join(uploads_dir, path)

        # if path is toplevel output dir, check for result tarball
        # if tarball exists, trigger output download
        if path.endswith('-output'):
            result_targz = '{0}.tar.gz'.format(path)
            result_path = op.join(uploads_dir, result_targz)
            if op.exists(result_path):
                return redirect(url_for('download', path=result_targz))

        # if result file not ready yet, let user browse the run directory
        if op.isdir(path_join):
            folder = Folder(uploads_dir, path)
            folder.read()
            return render_template('folder.html', folder=folder)
        else:
            my_file = File(uploads_dir, path)
            context = my_file.apply_action(View)
            folder = Folder(uploads_dir, my_file.get_path())
            if context == None:
                return render_template('file_unreadable.html', folder=folder)
            return render_template('file_view.html', text=context['text'], file=my_file, folder=folder)

    @app.route('/download/<path:path>')
    def download(path=''):
        return send_from_directory(app.config['UPLOADS_DIRECTORY'], path)

    @app.route('/download_sample_data')
    def sample_data():
        from shutil import make_archive

        sample_data_dir = 'Sample_Data'
        sample_data_path = op.join(SCRIPT_PATH, 'pipeline', sample_data_dir)
        sample_data_zip_base = op.join(app.config['UPLOADS_DIRECTORY'], sample_data_dir)
        make_archive(sample_data_zip_base, format="gztar", root_dir=sample_data_path)

        return redirect(url_for('download', path='{0}.tar.gz'.format(sample_data_dir)))

    return app


if __name__ == '__main__':
    create_app(configfile='site.cfg').run(host='0.0.0.0')
