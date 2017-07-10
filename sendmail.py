#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

class EmailClient():
    def __init__(self, email_from='markerminer@gmail.com',
                 from_name='MarkerMiner', api_key='00000000-0000-0000-0000-0000000000000'):
        self.api_uri = 'https://api.elasticemail.com/v2'
        self.email_from = email_from
        self.from_name = from_name
        self.api_key = api_key

    def request(self, method, url, payload):
        payload['apikey'] = self.api_key
        if method == 'POST':
            result = requests.post(self.api_uri + url, params=payload)
        elif method == 'PUT':
            result = requests.put(self.api_uri + url, params=payload)
        elif method == 'GET':
            attach = ''
            for key in payload:
                attach = attach + key + '=' + payload[key] + '&'
            url = url + '?' + attach[:-1]
            result = requests.get(self.api_uri + url)
        response = result.json()
        if response['success'] is False:
            return response['error']
        return response['data']

    def _send_email(self, subject, email_from, from_name, email_to, body_html, body_text, is_txn):
        payload = {
            'subject': subject,
            'from': email_from,
            'fromName': from_name,
            'to': email_to,
            'bodyHtml': body_html,
            'bodyText': body_text,
            'isTransactional': is_txn
        }

        return self.request('POST', '/email/send', payload)

    def send_email(self, to_email, result_url):
        subject = 'MarkerMiner pipeline status: Submitted'

        email_text_html = """
Thank you for using the MarkerMiner pipeline.<br />
<br />
While the job is in progress, intermediate results and logs can be viewed here: {0} <br />
<br />
Once the job has run to completion you should receive an email notification.<br />
At this point, the above link will trigger the download of the pipeline output (in tar.gz.format).<br />
<br />
If you use MarkerMiner in your research, please cite us:<br />
<br />
Chamala, S., Garcia, N., Godden, G.T., Krishnakumar, V., Jordon-Thaden, I. E.,<br />
DeSmet, R., Barbazuk, W. B., Soltis, D.E., Soltis, P.S. (2015)<br />
MarkerMiner 1.0: A new application for phylogenetic marker development<br />
using angiosperm transcriptomes. Applications in Plant Sciences, 3(4): 1400115.<br />
        """.format(result_url)

        email_text = """
Thank you for using the MarkerMiner pipeline.

While the job is in progress, intermediate results and logs can be viewed here: {0}

Once the job has run to completion you should receive an email notification.
At this point, the above link will trigger the download of the pipeline output (in tar.gz.format).

If you use MarkerMiner in your research, please cite us:

Chamala, S., Garcia, N., Godden, G.T., Krishnakumar, V., Jordon-Thaden, I. E.,
DeSmet, R., Barbazuk, W. B., Soltis, D.E., Soltis, P.S. (2015)
MarkerMiner 1.0: A new application for phylogenetic marker development
using angiosperm transcriptomes. Applications in Plant Sciences, 3(4): 1400115.
        """.format(result_url)

        self._send_email(
            subject, self.email_from, self.from_name, to_email,
            email_text_html, email_text, True
        )
