# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
from bika.lims import api
from bika.lims import logger
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import create_analysisrequest
from collective.taskqueue.interfaces import ITaskQueue
from plone import api as ploneapi
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser import BrowserView
from smtplib import SMTPRecipientsRefused
from zope.component import queryUtility


class Async_AR_Utils(BrowserView):

    def async_create_analysisrequest(self):
        msgs = []
        form = self.request.form
        records = json.loads(form.get('records', '[]'))
        attachments = json.loads(form.get('attachments', '[]'))
        ARs = []
        logger.info('Async create %s records' % len(records))
        for n, record in enumerate(records):
            client_uid = record.get("Client")
            client = api.get_object_by_uid(client_uid)

            if not client:
                msgs.append("Error: Client {} found".format(client_uid))
                continue

            # get the specifications and pass them directly to the AR
            # create function.
            specifications = record.pop("Specifications", {})

            # Create the Analysis Request
            ar = create_analysisrequest(
                client,
                self.request,
                values=record,
                specifications=specifications)
            ARs.append(ar.getId())

            _attachments = []
            for att_uid in attachments.get(str(n), []):
                attachment = api.get_object_by_uid(att_uid)
                _attachments.append(attachment)
            if _attachments:
                ar.setAttachment(_attachments)

        if len(ARs) == 1:
            msgs.append('Created AR {}'.format(ARs[0]))
        elif len(ARs) > 1:
            msgs.append('Created ARs {}'.format(', '.join(ARs)))
        else:
            msgs.append('No ARs created')
        message = '; '.join(msgs)
        logger.info('AR Creation complete: {}'.format(message))
        self._email_analyst(message)
        return

    def queue_count(self):
        task_queue = queryUtility(ITaskQueue, name='ar-create')
        if task_queue is None:
            return 0
        return 'Len = %s' % len(task_queue)

    def _email_analyst(self, message):
        mail_template = """
Dear {name},

Analysis request creation completed with the following messages:
{message}

Cheers
Bika LIMS
"""
        member = ploneapi.user.get_current()
        mail_host = ploneapi.portal.get_tool(name='MailHost')
        from_email = mail_host.email_from_address
        to_email = member.getProperty('email')
        subject = 'AR Creation Complete'
        if len(to_email) == 0:
            to_email = from_email
            subject = 'AR Creation by admin user is complete'
        mail_text = mail_template.format(
            name=member.getProperty('fullname'),
            message=message)
        try:
            return mail_host.send(
                mail_text, to_email, from_email,
                subject=subject, charset="utf-8", immediate=False)
        except SMTPRecipientsRefused:
            raise SMTPRecipientsRefused('Recipient address rejected by server')
