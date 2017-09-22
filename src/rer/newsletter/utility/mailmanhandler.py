# -*- coding: utf-8 -*-
from zope.interface import Interface, implements
# from json import dumps


class IMailmanHandler(Interface):
    ''' Interface for mailman handler '''


class MailmanHandler(object):
    implements(IMailmanHandler)
    ''' utility class to comunicate with mailman server '''

    def subscribe(self, mail):
        print mail
        return True

    def unsubscribe(self, mail):
        print mail
        return True

    def sendMessage(self, message):
        print message
        # vedere se organizzare o meno le eccezioni
        # response = {}
        # response['error'] = "Problem with server comunication"
        #
        # return dumps(response)
        return True
