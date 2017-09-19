from zope.component import getUtility
from rer.newsletter.utility.mailmanhandler import IMailmanHandler


def changeMessageState(message, event):

    if event.action == 'send':

        try:
            mh = getUtility(IMailmanHandler)
            mh.sendMessage(message.text.output)
        except Exception:
            # trovare modo di gestire il ritorno di qualcosa che e andato storto
            raise Exception("Problem with server comunication")

        # guardare se usare eccezioni
        # oppure fare cio con i messaggi di errore
