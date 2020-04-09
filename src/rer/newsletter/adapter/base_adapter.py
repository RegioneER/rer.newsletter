# -*- coding: utf-8 -*-
from rer.newsletter import logger
from rer.newsletter.utility.channel import IChannelUtility
from zope.interface import implementer
from zope.interface import Interface
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import INVALID_CHANNEL

import json


class IChannelSender(Interface):
    """Marker interface to provide a video embed html code"""


@implementer(IChannelSender)
class BaseAdapter(object):
    """ Adapter standard di base, invio sincrono usando plone
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def unsubscribe(self, channel, mail):
        logger.error('DEBUG: unsubscribe %s %s', channel, mail)
        return True

    def sendMessage(self, channel, message, unsubscribe_footer=None):
        logger.error('DEBUG: sendMessage %s %s', channel, message)
        return True

    def addChannel(self, channel):
        logger.error('DEBUG: addChannel %s', channel)
        return True

    def importUsersList(self, usersList, channel):
        logger.error('DEBUG: import userslist %s in %s', usersList, channel)
        return True

    def emptyChannelUsersList(self, channel):
        # vedere logica per eliminazione dell'intera lista di utenti di una nl
        logger.error('DEBUG: emptyChannelUsersList %s', channel)
        return True

    def deleteUser(self, mail, channel):
        logger.error(
            'DEBUG: delete user %s from channel %s',
            mail,
            channel
        )
        return True

    def exportUsersList(self, channel):
        logger.error('DEBUG: export users of channel: %s', channel)
        response = []

        element = {}
        element['id'] = 1
        element['Emails'] = 'cicci@balicci.it'
        response.append(element)

        element = {}
        element['id'] = 2
        element['Emails'] = 'saluti@baci.it'
        response.append(element)

        return json.dumps(response), OK

    def deleteUserList(self, usersList, channel):
        logger.error('delete userslist %s from %s',
                     usersList, channel)
        return True

    def getNumActiveSubscribers(self, channel):
        logger.error('Get number of active subscribers from %s', channel)

        return 3, OK
