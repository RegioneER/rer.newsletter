from plone import api
from plone.restapi.services import Service
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
from zope.component import getUtility


class SubscribersListGet(Service):

    def reply(self):
        """
        """
        status = UNHANDLED
        channel = self.context.id_channel

        api_channel = getUtility(IChannelUtility)
        userList, status = api_channel.exportUsersList(channel)

        if status == OK:
            return userList
