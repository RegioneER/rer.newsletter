# -*- coding: utf-8 -*-
from zope.component import getUtility
from rer.newsletter.utility.newsletter import INewsletterUtility

# eccezioni per mail
from smtplib import SMTPRecipientsRefused

# messaggi standard della form di dexterity
# from Products.statusmessages.interfaces import IStatusMessage
# from plone.dexterity.i18n import MessageFactory as dmf


def changeMessageState(message, event):

    if event.action == 'send':

        try:

            utility = getUtility(INewsletterUtility)
            utility.sendMessage(message.aq_parent.id_newsletter, message)

        # queste eccezioni devono tornare come status message, non bloccare il programma
        except SMTPRecipientsRefused:
            raise SMTPRecipientsRefused(u"Problemi con l'invio del messaggio")
        except Exception:
            raise Exception("Problem with server comunication")
