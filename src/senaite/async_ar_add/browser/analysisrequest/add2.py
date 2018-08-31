from bika.lims import api
from bika.lims.browser.analysisrequest.add2 import \
    ajaxAnalysisRequestAddView as ajaxARAV

from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implements

from bika.lims.utils.analysisrequest import create_analysisrequest as crar
from collections import OrderedDict

from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import tmpID
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _


class ajaxAnalysisRequestAddView(ajaxARAV):
    implements(IPublishTraverse)

    def ajax_submit(self):
        """Submit & create the ARs
        """

        import pdb; pdb.set_trace()
        # Get AR required fields (including extended fields)
        fields = self.get_ar_fields()

        # extract records from request
        records = self.get_records()

        fielderrors = {}
        errors = {"message": "", "fielderrors": {}}

        attachments = {}
        valid_records = []

        # Validate required fields
        for n, record in enumerate(records):

            # Process UID fields first and set their values to the linked field
            uid_fields = filter(lambda f: f.endswith("_uid"), record)
            for field in uid_fields:
                name = field.replace("_uid", "")
                value = record.get(field)
                if "," in value:
                    value = value.split(",")
                record[name] = value

            # Extract file uploads (fields ending with _file)
            # These files will be added later as attachments
            file_fields = filter(lambda f: f.endswith("_file"), record)
            attachments[n] = map(lambda f: record.pop(f), file_fields)

            # Process Specifications field (dictionary like records instance).
            # -> Convert to a standard Python dictionary.
            specifications = map(
                lambda x: dict(x), record.pop("Specifications", []))
            record["Specifications"] = specifications

            # Required fields and their values
            required_keys = [field.getName() for field in fields
                             if field.required]
            required_values = [record.get(key) for key in required_keys]
            required_fields = dict(zip(required_keys, required_values))

            # Client field is required but hidden in the AR Add form. We remove
            # it therefore from the list of required fields to let empty
            # columns pass the required check below.
            if record.get("Client", False):
                required_fields.pop('Client', None)

            # Contacts get pre-filled out if only one contact exists.
            # We won't force those columns with only the Contact filled out to
            # be required.
            contact = required_fields.pop("Contact", None)

            # None of the required fields are filled, skip this record
            if not any(required_fields.values()):
                continue

            # Re-add the Contact
            required_fields["Contact"] = contact

            # Missing required fields
            missing = [f for f in required_fields if not record.get(f, None)]

            # If there are required fields missing, flag an error
            for field in missing:
                fieldname = "{}-{}".format(field, n)
                msg = _("Field '{}' is required".format(field))
                fielderrors[fieldname] = msg

            # Selected Analysis UIDs
            selected_analysis_uids = record.get("Analyses", [])

            # Partitions defined in Template
            template_parts = {}
            template_uid = record.get("Template_uid")
            if template_uid:
                template = api.get_object_by_uid(template_uid)
                for part in template.getPartitions():
                    # remember the part setup by part_id
                    template_parts[part.get("part_id")] = part

            # The final data structure should look like this:
            # [{"part_id": "...", "container_uid": "...", "services": []}]
            partitions = {}
            parts = record.pop("Parts", [])
            for part in parts:
                part_id = part.get("part")
                service_uid = part.get("uid")
                # skip unselected Services
                if service_uid not in selected_analysis_uids:
                    continue
                # Container UID for this part
                container_uids = []
                template_part = template_parts.get(part_id)
                if template_part:
                    container_uid = template_part.get("container_uid")
                    if container_uid:
                        container_uids.append(container_uid)

                # remember the part id and the services
                if part_id not in partitions:
                    partitions[part_id] = {
                        "part_id": part_id,
                        "container_uid": container_uids,
                        "services": [service_uid],
                    }
                else:
                    partitions[part_id]["services"].append(service_uid)

            # Inject the Partitions to the record (will be picked up during the
            # AR creation)
            record["Partitions"] = partitions.values()

            # Process valid record
            valid_record = dict()
            for fieldname, fieldvalue in record.iteritems():
                # clean empty
                if fieldvalue in ['', None]:
                    continue
                valid_record[fieldname] = fieldvalue

            # append the valid record to the list of valid records
            valid_records.append(valid_record)

        # return immediately with an error response if some field checks failed
        if fielderrors:
            errors["fielderrors"] = fielderrors
            return {'errors': errors}

        # Process Form
        ARs = OrderedDict()
        for n, record in enumerate(valid_records):
            client_uid = record.get("Client")
            client = self.get_object_by_uid(client_uid)

            if not client:
                raise RuntimeError("No client found")

            # get the specifications and pass them to the AR create function.
            specifications = record.pop("Specifications", {})

            # Create the Analysis Request
            try:
                ar = crar(
                    client,
                    self.request,
                    record,
                    specifications=specifications
                )
            except (KeyError, RuntimeError) as e:
                errors["message"] = e.message
                return {"errors": errors}
            # We keep the title to check if AR is newly created
            # and UID to print stickers
            ARs[ar.Title()] = ar.UID()

            _attachments = []
            for attachment in attachments.get(n, []):
                if not attachment.filename:
                    continue
                att = _createObjectByType("Attachment", client, tmpID())
                att.setAttachmentFile(attachment)
                att.processForm()
                _attachments.append(att)
            if _attachments:
                ar.setAttachment(_attachments)

        level = "info"
        if len(ARs) == 0:
            message = _('No Analysis Requests could be created.')
            level = "error"
        elif len(ARs) > 1:
            message = _('Analysis requests ${ARs} were successfully created.',
                        mapping={'ARs': safe_unicode(', '.join(ARs.keys()))})
        else:
            message = _('Analysis request ${AR} was successfully created.',
                        mapping={'AR': safe_unicode(ARs.keys()[0])})

        # Display a portal message
        self.context.plone_utils.addPortalMessage(message, level)
        # Automatic label printing won't print "register" labels for sec. ARs
        bika_setup = api.get_bika_setup()
        auto_print = bika_setup.getAutoPrintStickers()

        # https://github.com/bikalabs/bika.lims/pull/2153
        new_ars = [uid for key, uid in ARs.items() if key[-1] == '1']

        if 'register' in auto_print and new_ars:
            return {
                'success': message,
                'stickers': new_ars,
                'stickertemplate': bika_setup.getAutoStickerTemplate()
            }
        else:
            return {'success': message}
