# -*- coding: utf-8 -*-
from zope.interface import Interface

# general
UNHANDLED = 0
SUBSCRIBED = OK = 1
INVALID_NEWSLETTER = 5

# subscribe
ALREADY_SUBSCRIBED = 2
INVALID_EMAIL = 3

# unsubscribe
INEXISTENT_MAIL = 4


class INewsletterUtility(Interface):
    """ """

    def subscribe(newsletter, mail):
        """
        Subscribe to newsletter

        Args:
            newsletter (str): newsletter id
            mail (str): email address

        Returns:
            int: OK (1) if succesful,
                 ALREADY_SUBSCRIBED (2),
                 INVALID_NEWSLETTER (5) newsletter not found,
                 INVALID_EMAIL (3) problem with mail.

        Raises:
        """

    def unsubscribe(self, newsletter, mail):
        """
        Unsubscribe from newsletter

        Args:
            newsletter (str): newsletter id
            mail (str): email address

        Returns:
            int: OK (1) if succesful,
                 INVALID_NEWSLETTER (5) newsletter not found,
                 INEXISTENT_MAIL (4) mail not found.

        Raises:
        """

    def sendMessage(self, newsletter, message):
        """
        Send message to mailman server

        Args:
            newsletter (str): newsletter id
            message (str): message

        Returns:
            int: OK (1) if succesful,
                 INVALID_NEWSLETTER (5) newsletter not found.

        Raises:
        """
