# -*- coding: utf-8 -*-
from zope.component import getUtility
from rer.newsletter.utility.newsletter import INewsletterUtility


def changeMessageState(message, event):

    if event.action == 'send':

        try:
            nl = getUtility(INewsletterUtility)
            # in questo punto devo andare a compilare la mail con il messaggio
            # e tutte le componenti della newsletter
            nl.sendMessage(message.text.output)
        except Exception:
            # trovare modo di gestire il ritorno di qualcosa che e andato storto
            # vedere come gestire bene l'eccezione qui dentro
            raise Exception("Problem with server comunication")
