# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import senaite.async_ar_add


class SenaiteAsyncArAddLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=senaite.async_ar_add)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'senaite.async_ar_add:default')


SENAITE_ASYNC_AR_ADD_FIXTURE = SenaiteAsyncArAddLayer()


SENAITE_ASYNC_AR_ADD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SENAITE_ASYNC_AR_ADD_FIXTURE,),
    name='SenaiteAsyncArAddLayer:IntegrationTesting'
)


SENAITE_ASYNC_AR_ADD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SENAITE_ASYNC_AR_ADD_FIXTURE,),
    name='SenaiteAsyncArAddLayer:FunctionalTesting'
)


SENAITE_ASYNC_AR_ADD_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        SENAITE_ASYNC_AR_ADD_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='SenaiteAsyncArAddLayer:AcceptanceTesting'
)
