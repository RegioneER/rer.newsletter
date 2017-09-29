# -*- coding: utf-8 -*-
from mailmanclient._client import HTTPError
from mailmanclient import Client
from mailmanclient import MailmanConnectionError
from zope.interface import implements

from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import ALREADY_SUBSCRIBED, SUBSCRIBED

# TODO: move to p.a.registry or zope.conf
# Please note that port ‘9001’ is used above, since mailman’s test server
# runs on port 9001. In production Mailman’s REST API usually listens
# on port 8001.
API_ENDPOINT = 'http://localhost:9001/3.1'
API_USERNAME = 'restadmin'
API_PASSWORD = 'restpass'


class MailmanHandler(object):
    implements(INewsletterUtility)
    '''utility class to comunicate with mailman server'''

    def _api(self):
        try:
            return Client(API_ENDPOINT, API_USERNAME, API_PASSWORD)
        except MailmanConnectionError:
            logger.error('Could not connect to Mailman API %s', API_ENDPOINT)
            # raise
            return None

    def lists(self):
        # TODO
        client = self._api()
        return client.lists

    def subscribe(self, newsletter, mail, name=None):
        client = self._api()
        if not client:
            logger.warning("TODO: raise exception")
            logger.warning("fake %s %s subscription", newsletter, mail)
            return SUBSCRIBED
        _list = client.get_list(newsletter)
        try:
            _data = _list.subscribe(
                mail,
                name or mail,
                pre_verified=False,
                pre_approved=False
            )
            logger.info("DEBUG: %s", _data)
            # {u'token_owner': u'subscriber',
            #   u'http_etag': u'"2f1dfffd552b1a6a0514ad416d4e426d8c927d44"',
            #   u'token': u'0000000000000000000000000000000000000001'}
        except HTTPError as exc:
            if exc.code == 409:
                logger.info("DEBUG: %s", exc)
                return ALREADY_SUBSCRIBED
        return SUBSCRIBED

    def unsubscribe(self, newsletter, mail):
        logger.info("DEBUG: unsubscribe %s %s", newsletter, mail)
        return True

    def sendMessage(self, newsletter, message):
        logger.info("DEBUG: sendMessage %s %s", newsletter, message)
        return True

    def addNewsletter(self, newsletter):
        logger.info("DEBUG: addNewsletter %s", newsletter)
        return True
