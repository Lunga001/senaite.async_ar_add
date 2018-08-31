# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory
from bika.lims.permissions import ADD_CONTENT_PERMISSIONS
from bika.lims.permissions import ADD_CONTENT_PERMISSION
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore.utils import ContentInit


_ = MessageFactory('senaite.async_ar_add')

# -*- extra stuff goes here -*-

PROJECTNAME = 'senaite.async_ar_add'


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    allTypes = zip(content_types, constructors, ftis)
    for atype, constructor, fti in allTypes:
        kind = "%s: Add %s" % (PROJECTNAME, atype.portal_type)
        perm = ADD_CONTENT_PERMISSIONS.get(
            atype.portal_type, ADD_CONTENT_PERMISSION)
        ContentInit(kind,
                    content_types=(atype,),
                    permission=perm,
                    extra_constructors=(constructor,),
                    fti=fti,
                    ).initialize(context)
