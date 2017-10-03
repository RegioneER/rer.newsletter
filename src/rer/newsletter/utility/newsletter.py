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

# add newsletter
NEWSLETTER_USED = 6

# import usersList
FILE_FORMAT = 7


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

    def unsubscribe(newsletter, mail):
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

    def sendMessage(newsletter, message):
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

    def addNewsletter(newsletter):
        """
        add new newsletter to mailman server

        Args:
            newsletter (str): newsletter id

        Returns:
            int: OK (1) if succesful,
                 NEWSLETTER_USED (6) newsletter already used.

        Raised:
        """

    def importUsersList(usersList):
        """
        import list of email

        Args:
            usersList (list): email

        Returns:
            int: OK (1) if succesful,
                 FILE_FORMAT (7) if incorrect format file,

        Raised:
        """
