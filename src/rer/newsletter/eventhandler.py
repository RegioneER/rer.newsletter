# -*- coding: utf-8 -*-
from zope.component import getUtility
from rer.newsletter.utility.newsletter import INewsletterUtility


def changeMessageState(message, event):

    if event.action == 'send':

        try:
            nl = getUtility(INewsletterUtility)
            nl.sendMessage(message.text.output)
        except Exception:
            # trovare modo di gestire il ritorno di qualcosa che e andato storto
            raise Exception("Problem with server comunication")

        # guardare se usare eccezioni
        # oppure fare cio con i messaggi di errore
