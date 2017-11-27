# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'rer.newsletter:uninstall',
        ]


def post_install(context):
    """Post install script"""
    import pdb
    pdb.set_trace()

    pass


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
