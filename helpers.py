#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as op
import sys
import errno
import re
from os import error

from werkzeug.utils import secure_filename



SCRIPT_PATH = op.dirname(op.abspath(__file__))
ALLOWED_EXTENSIONS = ['fa', 'fasta', 'fsa', 'fna', 'txt']
ORGANISMS = []
fp = open(op.join(SCRIPT_PATH, 'pipeline', 'Resources', 'organisms.tsv'), 'r')
for line in fp:
    o = line.split('\t')
    ORGANISMS.append((o[0], o[1]))
fp.close()
ORGANISMS.sort(key=lambda x:x[0], reverse=False)


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


def mkdir_p(dir):
    try:
        os.makedirs(dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and op.isdir(dir):
            pass
        else: raise


def build_job_cmd(form, upload_dir, results_dir, debug=False):
    job_cmd = [sys.executable, \
        op.join(SCRIPT_PATH, 'pipeline', 'markerMiner.py'), \
        '-transcriptFilesDir', upload_dir, \
        '-singleCopyReference', form.singleCopyReference.data, \
        '-minTranscriptLen', form.minTranscriptLen.data, \
        '-minProteinCoverage', form.minProteinCoverage.data, \
        '-minTranscriptCoverage', form.minTranscriptCoverage.data, \
        '-minSimilarity', form.minSimilarity.data, \
        '-cpus', form.cpus.data, \
        '-outputDirPath', results_dir]
    if form.email.data:
        job_cmd.extend(['-email', '"{0}"'.format(form.email.data)])
    if debug:
        job_cmd.append('-debug')
    return ' '.join(str(x) for x in job_cmd)


def upload_files(form, dir):
    files = []
    for data in form.fileupload.raw_data:
        filename = secure_filename(data.filename)
        if filename not in files:
            data.save(op.join(dir, filename))
            files.append(filename)
    return


def get_result_url(request, job_id):
    output_basename = '{0}-output'.format(job_id)
    result_url = op.join(request.url_root, 'results', output_basename)

    return result_url
