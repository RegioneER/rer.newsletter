# -*- coding: utf-8 -*-
from smtplib import SMTPRecipientsRefused
from zope.component import getUtility

from rer.newsletter.utility.newsletter import INewsletterUtility

# messaggi standard della form di dexterity
# from Products.statusmessages.interfaces import IStatusMessage
# from plone.dexterity.i18n import MessageFactory as dmf


def changeMessageState(message, event):
    if event.action == 'send':
        try:
            utility = getUtility(INewsletterUtility)
            utility.sendMessage(message.aq_parent.id_newsletter, message)
        except SMTPRecipientsRefused:
            raise SMTPRecipientsRefused(u"Problemi con l'invio del messaggio")
