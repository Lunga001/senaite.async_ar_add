from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from ace.lims import aceMessageFactory as _
# from bika.lims.fields import ExtReferenceField, ExtStringField
# from bika.lims.browser.widgets import ReferenceWidget as bikaReferenceWidget
from bika.lims.fields import ExtIntegerField
from bika.lims.interfaces import IBikaSetup
from Products.Archetypes.public import *
from Products.Archetypes.atapi import IntegerWidget
# from Products.CMFCore import permissions
from zope.component import adapts
from zope.interface import implements


class BikaSetupSchemaExtender(object):
    adapts(IBikaSetup)
    implements(IOrderableSchemaExtender)

    fields = [

        ExtIntegerField(
            'MaxARsBeforeAsync',
            schemata="Analyses",
            required=0,
            default=1,
            widget=IntegerWidget(
                label=_("Maximum number of ARs before Async."),
                description=_("If a user initiates the creation of more ARs than this number, they will be created in the background and an email will notify them when they are all created"),
            )
        ),

    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields


class BikaSetupSchemaModifier(object):
    adapts(IBikaSetup)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        return schema
