#!/usr/bin/env python

import os
import os.path as op
from multiprocessing import cpu_count

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import TextField, IntegerField, FloatField, SelectField, \
    FormField, SubmitField, ValidationError, validators
from wtforms.validators import Required


choices = [(x, "{0}. {1}".format(x[:1], x[1:])) for x in \
    os.listdir(op.join(op.dirname(__file__), 'pipeline', 'Resources'))]
allowed_files = ['fa', 'fasta', 'fsa', 'fna', 'txt']


class JobSubmitForm(Form):
    fileupload = FileField('Input FASTA file', validators=[
        FileRequired(),
        FileAllowed(allowed_files, 'Plain-text FASTA files only!')
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

    submit_button = SubmitField('Submit Job')


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)

    app.config['SECRET_KEY'] = '\xb4jzK\xa1\xf9\xaa\xc8D\xb9X\xaa\xd4\x9b\xef\xd6P\xef\x18-\x0f\xd5\xe0m'

    @app.route('/', methods=('GET', 'POST'))
    def index():
        form = JobSubmitForm(singleCopyReference="Athaliana" , minTranscriptLen=900, \
            minProteinCoverage=80, minTranscriptCoverage=70, \
            minSimilarity=70, cpus=3, enctype="multipart/form-data")
        if form.validate_on_submit(): # to get error messages to the browser
            filename = secure_filename(form.fileupload.data.filename)
        return render_template('index.html', form=form)

    return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', debug=True)
