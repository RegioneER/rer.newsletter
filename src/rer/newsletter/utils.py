# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api


def addToHistory(message):
    """ Add to history that message is sent """
    # rt = api.portal.get_tool(name='portal_repository')
    if not message:
        return []

    def new_history_row(message):
        return dict(
            action=u'Invio',
            review_state=api.content.get_state(obj=message),
            actor=api.user.get_current().get('username', None),
            comment=u'',
            time=DateTime()
        )
    list_history = [
        x for x in message.workflow_history.get('message_workflow')]
    list_history.append(new_history_row(message))
    message.workflow_history['message_workflow'] = tuple(list_history)
