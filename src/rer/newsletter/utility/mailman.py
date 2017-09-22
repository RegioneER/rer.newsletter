# -*- coding: utf-8 -*-
import logging
from mailmanclient import Client
from mailmanclient import MailmanConnectionError
from zope.interface import implements

from rer.newsletter.utility.newsletter import INewsletterUtility

logger = logging.getLogger(__name__)

# TODO: move to p.a.registry or zope.conf
API_ENDPOINT = 'http://localhost:8001/3.1'
API_USERNAME = 'restadmin'
API_PASSWORD = 'restpass'


class MailmanHandler(object):
    implements(INewsletterUtility)
    '''utility class to comunicate with mailman server'''

    def client(self):
        try:
            return Client(API_ENDPOINT, API_USERNAME, API_PASSWORD)
        except MailmanConnectionError:
            logger.error('Could not connect to Mailman API %s', API_ENDPOINT)
            raise

    def subscribe(self, newsletter, mail):
        print newsletter
        print mail
        return True

    def unsubscribe(self, newsletter, mail):
        print newsletter
        print mail
        return True

    def sendMessage(self, newsletter, message):
        print newsletter
        print message
        # vedere se organizzare o meno le eccezioni
        # response = {}
        # response['error'] = "Problem with server comunication"
        #
        # return dumps(response)
        return True
