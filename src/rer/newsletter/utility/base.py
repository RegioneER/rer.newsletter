from zope.interface import implements
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import OK, ALREADY_SUBSCRIBED, INVALID_NEWSLETTER, INVALID_EMAIL, INEXISTENT_EMAIL, MAIL_NOT_PRESENT, INVALID_SECRET, ALREADY_ACTIVE
import json
import re

# api
from plone import api

# annotations
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations

# for calculate email uuid
from zope.component import getUtility
from plone.uuid.interfaces import IUUIDGenerator

# datetime
from datetime import datetime, timedelta

# premailer
from premailer import transform

# eccezioni per mail
from smtplib import SMTPRecipientsRefused

# Invalid
from zope.interface import Invalid

KEY = "rer.newsletter.subscribers"


def mailValidation(mail):
    # valido la mail
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        raise Invalid(_(u"generic_problem_email_validation", default=u"Una o piu delle mail inserite non sono valide"))
    return True


def uuidValidation(uuid):
    match = re.match('[0-9a-f]{32}\Z', uuid)
    if match is None:
        return False
    return True


def isCreationDateExpired(creation_date):
    # settare una data di scadenza di configurazione
    if (datetime.today() - datetime.strptime(creation_date, '%d/%m/%Y %H:%M:%S')) < timedelta(days=2):
        return True
    return False


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
            annotations[KEY] = PersistentList([])
        self.annotations = annotations[KEY]

        return nl[0].getObject()

    def activeUser(self, newsletter, secret):
        logger.info("DEBUG: active user in %s", newsletter)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        # valido il secret
        if not uuidValidation(secret):
            return INVALID_SECRET

        # attivo l'utente
        count = 0
        element_id = None
        for user in self.annotations:
            if user['token'] == secret:
                if user['is_active']:
                    return ALREADY_ACTIVE
                else:
                    element_id = count
                    break
            count += 1

        if element_id is not None:
            self.annotations[element_id]['is_active'] = True
            return OK
        else:
            return INVALID_SECRET

    def importUsersList(self, usersList, newsletter):
        logger.info("DEBUG: import userslist %s in %s", usersList, newsletter)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        # controllo che tutte le mail siano valide
        # come mi devo comportare se ci sono mail che non sono valide ?
        for user in usersList:
            if not mailValidation(user):
                return INVALID_EMAIL

        # calculate new uuid for email
        generator = getUtility(IUUIDGenerator)
        uuid = generator()

        for user in usersList:
            if user not in self.annotations:
                self.annotations.append(PersistentDict({
                    'email': user,
                    'is_active': True,
                    'token': uuid,
                    'creation_date': datetime.today().strftime('%d/%m/%Y %H:%M:%S'),
                }))

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
            element['email'] = user['email']
            element['is_active'] = user['is_active']
            element['creation_date'] = user['creation_date']
            response.append(element)
            c += 1

        return json.dumps(response), OK

    def deleteUser(self, newsletter, mail):
        logger.info("DEBUG: delete user %s from newsletter %s", mail, newsletter)
        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        try:
            element_id = None
            count = 0
            for user in self.annotations:
                if user['email'] == mail:
                    element_id = count
                    break
                count += 1

            # elimino persona dalla newsletter
            if element_id is not None:
                self.annotations.pop(element_id)
            else:
                raise ValueError
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
                element_id = None
                count = 0
                for u in self.annotations:
                    if u['email'] == user:
                        element_id = count
                        break
                    count += 1

                if element_id is not None:
                    self.annotations.pop(element_id)

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
            element_id = None
            count = 0
            for user in self.annotations:
                if user['email'] == mail:
                    element_id = count
                    break
                count += 1

            # elimino persona dalla newsletter
            if element_id is not None:
                self.annotations.pop(element_id)
            else:
                raise ValueError

        except ValueError:
            return INEXISTENT_EMAIL

        return OK

    def addUser(self, newsletter, mail):
        logger.info("DEBUG: add user: %s %s", newsletter, mail)
        nl = self._api(newsletter)

        if not nl:
            return INVALID_NEWSLETTER

        if not mailValidation(mail):
            return INVALID_EMAIL

        # calculate new uuid for email
        generator = getUtility(IUUIDGenerator)
        uuid = generator()

        # controllo che la mail non sia gia presente e attiva nel db
        for user in self.annotations:
            if (mail == user['email'] and user['is_active']) or (mail == user['email'] and not user['is_active'] and isCreationDateExpired(user['creation_date'])):
                return ALREADY_SUBSCRIBED
        else:
            self.annotations.append(PersistentDict({
                'email': mail,
                'is_active': True,
                'token': uuid,
                'creation_date': datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            }))

        return OK

    def subscribe(self, newsletter, mail, name=None):
        logger.info("DEBUG: subscribe %s %s", newsletter, mail)
        nl = self._api(newsletter)

        if not nl:
            return INVALID_NEWSLETTER, None

        if not mailValidation(mail):
            return INVALID_EMAIL, None

        # calculate new uuid for email
        generator = getUtility(IUUIDGenerator)
        uuid = generator()

        for user in self.annotations:
            if (mail == user['email'] and user['is_active']) or (mail == user['email'] and not user['is_active'] and isCreationDateExpired(user['creation_date'])):
                return ALREADY_SUBSCRIBED, None
        else:
            self.annotations.append(PersistentDict({
                'email': mail,
                'is_active': False,
                'token': uuid,
                'creation_date': datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            }))

        return OK, uuid

    def sendMessage(self, newsletter, message):
        logger.info("DEBUG: sendMessage %s %s", newsletter, message.title)

        nl = self._api(newsletter)
        if not nl:
            return INVALID_NEWSLETTER

        # costruisco il messaggio
        email = ''

        email = nl.header.raw
        email += '<style> ' + nl.css_style + '</style>'
        email += message.text.raw
        email += nl.footer.raw

        email = transform(email)

        # risolvo tutti gli uuid
        resolveuid = re.findall('(?<=resolveuid\/)(.*?)(?=\/)', email)
        catalog = api.portal.get_tool(name='portal_catalog')
        # controllare se in questo modo viene perfetta sempre
        for uuid in resolveuid:
            res = catalog.unrestrictedSearchResults(UID=uuid)
            if res:
                email = email.replace(
                    '../resolveuid/' + uuid, res[0].getURL()
                )

        try:
            # invio la mail ad ogni utente
            for user in self.annotations:
                mailHost = api.portal.get_tool(name='MailHost')
                mailHost.send(
                    email,
                    mto=user['email'],
                    mfrom='noreply@rer.it',
                    subject=nl.title,
                    charset='utf-8',
                    msg_type='text/html'
                    )
        except SMTPRecipientsRefused:
            raise SMTPRecipientsRefused

        return OK
