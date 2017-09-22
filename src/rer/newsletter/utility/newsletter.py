# -*- coding: utf-8 -*-
from zope.interface import Interface

UNHANDLED = 0
SUBSCRIBED = 1
ALREADY_SUBSCRIBED = 2
INVALID_EMAIL = 3


class INewsletterUtility(Interface):
    """ """

    def subscribe(newsletter, mail):
        """Subscribe to newsletter

        Args:
            newsletter (str): newsletter id
            mail (str): email address

        Returns:
            int: SUBSCRIBED (1) if succesful, ALREADY_SUBSCRIBED (2),
                INVALD_EMAIL (3) otherwise.

        Raises:
        """
