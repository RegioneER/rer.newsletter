from zope.component import getUtility
from rer.newsletter.utility.mailmanhandler import IMailmanHandler


def changeMessageState(message, event):

    if event.action == 'send':

        try:
            mh = getUtility(IMailmanHandler)
            mh.subscribe(message.text.output)
        except Exception:
            # trovare modo di gestire il ritorno di qualcosa che e andato storto
            # import pdb; pdb.set_trace()
            pass
