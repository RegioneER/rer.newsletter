# -*- coding: utf-8 -*-
from zope.interface import Interface

# general
UNHANDLED = 0
SUBSCRIBED = OK = 1
INVALID_CHANNEL = 5

# subscribe
ALREADY_SUBSCRIBED = 2
INVALID_EMAIL = 3

# Email
PROBLEM_WITH_MAIL = 11

# unsubscribe
INEXISTENT_EMAIL = 4

# add channel
CHANNEL_USED = 6

# import usersList
FILE_FORMAT = 7

# delete user
MAIL_NOT_PRESENT = 8

# user's activation
ALREADY_ACTIVE = 9
INVALID_SECRET = 10


class IChannelUtility(Interface):
    """ """

    def activeUser(channel, secret):
        """
        Active user

        Args:
            channel (str): channel id,
            secret (str): token for activation

        Returns:
            int: OK (1) if succesful,
                 ALREADY_ACTIVE (9),
                 INVALID_CHANNEL (5) channel not found,
                 INVALID_SECRET (10) problem with secret,
                 PROBLEM_WITH_MAIL (11) if errors are
                 present when email is sent.

        Raises:
        """

    def addUser(channel, mail):
        """
        Add user to channel from Admin side

        Args:
            channel (str): channel id,
            mail (str): email address

        Returns:
            int: OK (1) if succesful,
                 ALREADY_SUBSCRIBED (2),
                 INVALID_CHANNEL (5) channel not found,
                 INVALID_EMAIL (3) problem with mail.
            str: secret for autenticate user.

        Raises:
        """

    def subscribe(channel, mail):
        """
        Subscribe to channel

        Args:
            channel (str): channel id
            mail (str): email address

        Returns:
            int: OK (1) if succesful,
                 ALREADY_SUBSCRIBED (2),
                 INVALID_CHANNEL (5) channel not found,
                 INVALID_EMAIL (3) problem with mail.

        Raises:
        """

    def unsubscribe(channel, mail):
        """
        Unsubscribe from channel

        Args:
            channel (str): channel id
            mail (str): email address

        Returns:
            int: OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found,
                 INEXISTENT_MAIL (4) mail not found.

        Raises:
        """

    def sendMessage(channel, message):
        """
        Send message to mailman server

        Args:
            channel (str): channel id
            message (str): message

        Returns:
            int: OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found.

        Raises:
        """

    def getNumActiveSubscribers(channel):
        """
        Return number of subscribers for channel

        Args:
            channel (str): channel id

        Returns:
            (number of subscribers and status together)
            int: number of active subscribers and OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found.

        Raises:
        """

    def addChannel(channel):
        """
        add new channel to mailman server

        Args:
            channel (str): channel id

        Returns:
            int: OK (1) if succesful,
                 CHANNEL_USED (6) channel already used.

        Raised:
        """

    def importUsersList(usersList):
        """
        import list of email

        Args:
            usersList (list): email

        Returns:
            int: OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found,
                 INVALID_EMAIL (3) user's email not found.

        Raised:
        """

    def emptyChannelUsersList(channel):
        """
        empties channel users list

        Args:
            channel (str): channel id

        Returns:
            int: OK (1) if succesful,
                 INVALID_CHANNEL (5) channel not found.

        Raised:
        """

    def deleteUser(channel, email, secret):
        """
        delete a user from channel

        Args:
            mail (str): email
            channel (str): channel id

        Returns:
            int OK (1) if succesful,
                INVALID_CHANNEL (5) channel not found,
                MAIL_NOT_PRESENT (8) mail not present,
                PROBLEM_WITH_MAIL (11) if errors are
                present when email is sent.

        Raised:
        """

    def deleteUserList(usersList, channel):
        """
        delete a usersList from channel

        Args:
            usersList (list): email
            channel (str): channel id

        Returns:
            int OK (1) if succesful,
                INVALID_CHANNEL (5) channel not found,
                MAIL_NOT_PRESENT (8) user's email not found,
                INVALID_SECRET (10) user's secret not found.
        """

    def exportUsersList(channel):
        """
        export all user of channel

        Args:
            channel (str): channel id

        Returns:
            (List and Status together)
            list of string List of email if succesful,
            Int INVALID_CHANNEL (5) channel not found.

        Raised:
        """

    def getErrorMessage(code_error):
        """
        da scrivere
        """
