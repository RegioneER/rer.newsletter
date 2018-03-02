# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api

import pytz


def addToHistory(message):
    """ Add to history that message is sent """
    # rt = api.portal.get_tool(name='portal_repository')
    if not message:
        return []

    def new_history_row():
        return dict(
            action=u'Invio',
            review_state=u'Inviato',
            actor=api.user.get_current().get('username', None),
            comment=u'',
            time=datetime.now(pytz.timezone('Europe/Rome')
                              ).strftime('%Y/%m/%d %H:%M:%S.%f %z')
        )

    tuple_history = message.workflow_history.values()[0]
    list_history = [x for x in tuple_history]
    list_history.append(new_history_row())
    return tuple(list_history)
