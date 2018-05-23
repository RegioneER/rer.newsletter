# -*- coding: utf-8 -*-
from plone import api
from rer.newsletter import logger


default_profile = 'profile-orma.contenttypes:default'


def migrate_to_1001(context):
    setup_tool = api.portal.get_tool('portal_setup')
    setup_tool.runImportStepFromProfile(default_profile, 'plone.app.registry')
    logger.info(u'Updated to 1001')
