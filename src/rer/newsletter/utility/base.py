from zope.interface import implements
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK, ALREADY_SUBSCRIBED, INVALID_NEWSLETTER, INVALID_EMAIL, INEXISTENT_EMAIL, MAIL_NOT_PRESENT
import json

# api
from plone import api

# annotations
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
KEY = "rer.newsletter.subscribers"


def mailValidation(mail):

    # valido la mail
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        return False
    return True


class BaseHandler(object):
    implements(INewsletterUtility)
    """ utility class to send newsletter email with mailer of plone """

    # metodo privato
    def _api(self, newsletter):
        """ return Newsletter and initialize annotations """

        # controllo che il contesto sia la newsletter
        nl = api.content.find(
            portal_type='Newsletter',
            id_newsletter=newsletter
        )

        if not nl:
            # newsletter non prensete
            return None

        # controllo l'annotations della newsletter
        annotations = IAnnotations(nl[0].getObject())
        if KEY not in annotations.keys():
            # inizializzo l'annotations
            annotations[KEY] = PersistentList()
        self.annotations = annotations[KEY]

        return nl[0].getObject()

    def importUsersList(self, usersList, newsletter):
        logger.info("DEBUG: import userslist %s in %s", usersList, newsletter)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        # controllo che tutte le mail siano valide
        for user in usersList:
            if not mailValidation(user):
                return INVALID_EMAIL

        for user in usersList:
            if user not in self.annotations:
                    self.annotations.append(user)

        # catch exception
        return OK

    def exportUsersList(self, newsletter):
        logger.info("DEBUG: export users of newsletter: %s", newsletter)
        response = []
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        c = 0
        for user in self.annotations:
            element = {}
            element['id'] = c
            element['Emails'] = user
            response.append(element)
            c += 1

        return json.dumps(response), OK

    def deleteUser(self, newsletter, mail):
        logger.info("DEBUG: delete user %s from newsletter %s", mail, newsletter)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        try:
            self.annotations.remove(mail)
        except ValueError:
            return MAIL_NOT_PRESENT

        return OK

    def deleteUserList(self, usersList, newsletter):
        # manca il modo di far capire se una mail non e presente nella lista
        logger.info("DEBUG: delete userslist %s from %s", usersList, newsletter)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        for user in usersList:
            try:
                self.annotations.remove(user)
            except ValueError:
                # to handle
                pass

        return OK

    def emptyNewsletterUsersList(self, newsletter):
        logger.info("DEBUG: emptyNewsletterUsersList %s", newsletter)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        del self.annotations[:]

        return OK

    def unsubscribe(self, newsletter, mail):
        logger.info("DEBUG: unsubscribe %s %s", newsletter, mail)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        try:
            self.annotations.remove(mail)
        except ValueError:
            return INEXISTENT_EMAIL

        return OK

    def subscribe(self, newsletter, mail, name=None):
        logger.info("DEBUG: subscribe %s %s", newsletter, mail)
        nl = self._api(newsletter)

        if not nl:
            return INVALID_NEWSLETTER

        if not mailValidation(mail):
            return INVALID_EMAIL

        if mail not in self.annotations:
            self.annotations.append(mail)
        else:
            return ALREADY_SUBSCRIBED

        return OK

    def sendMessage(self, newsletter, message):
        logger.info("DEBUG: sendMessage %s %s", newsletter, message)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        return OK
