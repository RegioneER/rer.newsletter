# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from plone.registry.interfaces import IRegistry
from rer.agidtheme.base.interfaces import IRERSiteSchema
from rer.agidtheme.base.utility.interfaces import ICustomFields
from zope.component import getUtility


def addToHistory(message, active_users):
    """ Add to history that message is sent """
    # rt = api.portal.get_tool(name='portal_repository')
    if not message:
        return []

    def new_history_row(message, active_users):
        return dict(
            action=u'Invio',
            review_state=api.content.get_state(obj=message),
            actor=api.user.get_current().get('username', None),
            comments='Inviato il messaggio a ' +
            str(active_users) + ' utenti.',
            time=DateTime()
        )

    list_history = [
        x for x in message.workflow_history.get('message_workflow')]
    entry = new_history_row(message, active_users)
    list_history.append(entry)
    message.workflow_history['message_workflow'] = tuple(list_history)

    # message.modification_date = entry.get('time', None)
    # message.reindexObject(idxs=['modified'])


def get_site_title():
    registry = getUtility(IRegistry)
    try:
        site_settings = registry.forInterface(IRERSiteSchema,  # noqa
                                              prefix='plone',
                                              check=False)
        fields_value = getUtility(ICustomFields)
        return fields_value.titleLang(
            getattr(site_settings, 'site_title') or {})
    except Exception:
        return api.portal.get().title
