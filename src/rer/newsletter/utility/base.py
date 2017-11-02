# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.uuid.interfaces import IUUIDGenerator
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.newsletter import ALREADY_ACTIVE
from rer.newsletter.utility.newsletter import ALREADY_SUBSCRIBED
from rer.newsletter.utility.newsletter import INewsletterUtility
from rer.newsletter.utility.newsletter import INEXISTENT_EMAIL
from rer.newsletter.utility.newsletter import INVALID_EMAIL
from rer.newsletter.utility.newsletter import INVALID_NEWSLETTER
from rer.newsletter.utility.newsletter import INVALID_SECRET
from rer.newsletter.utility.newsletter import MAIL_NOT_PRESENT
from rer.newsletter.utility.newsletter import OK
from smtplib import SMTPRecipientsRefused
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Invalid

import json
import premailer
import re


KEY = 'rer.newsletter.subscribers'


def mailValidation(mail):
    # valido la mail
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]' +
        '+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        raise Invalid(
            _(
                u'generic_problem_email_validation',
                default=u'Una o piu delle mail inserite non sono valide'
            )
        )
    return True


def uuidValidation(uuid):
    match = re.match('[0-9a-f]{32}\Z', uuid)
    if match is None:
        return False
    return True


def isCreationDateExpired(creation_date):
    # settare una data di scadenza di configurazione
    cd_datetime = datetime.strptime(creation_date, '%d/%m/%Y %H:%M:%S')
    t = datetime.today() - cd_datetime
    if t < timedelta(days=2):
        return True
    return False


@implementer(INewsletterUtility)
class BaseHandler(object):
    ''' utility class to send newsletter email with mailer of plone '''

    def _storage(self, newsletter):
        obj = self._api(newsletter)
        if obj:
            annotations = IAnnotations(obj)
            if KEY not in annotations.keys():
                annotations[KEY] = PersistentList([])
            return annotations[KEY]

    def _api(self, newsletter):
        ''' return Newsletter and initialize annotations '''
        nl = api.content.find(
            portal_type='Newsletter',
            id_newsletter=newsletter
        )
        if not nl:
            return None
        obj = nl[0].getObject()
        return obj

    def activeUser(self, newsletter, secret):
        logger.info('DEBUG: active user in %s', newsletter)
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        # valido il secret
        if not uuidValidation(secret):
            return INVALID_SECRET

        # attivo l'utente
        count = 0
        element_id = None
        for user in annotations:
            if user['token'] == secret:
                if user['is_active']:
                    return ALREADY_ACTIVE
                else:
                    element_id = count
                    break
            count += 1

        if element_id is not None:
            annotations[element_id]['is_active'] = True
            return OK
        else:
            return INVALID_SECRET

    def importUsersList(self, usersList, newsletter):
        logger.info('DEBUG: import userslist %s in %s', usersList, newsletter)
        annotations = self._storage(newsletter)
        if annotations is None:
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
            if user not in annotations:
                annotations.append(PersistentDict({
                    'email': user,
                    'is_active': True,
                    'token': uuid,
                    'creation_date': datetime.today().strftime(
                        '%d/%m/%Y %H:%M:%S'
                    ),
                }))

        # catch exception
        return OK

    def exportUsersList(self, newsletter):
        logger.info('DEBUG: export users of newsletter: %s', newsletter)
        response = []
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        c = 0
        for user in annotations:
            element = {}
            element['id'] = c
            element['email'] = user['email']
            element['is_active'] = user['is_active']
            element['creation_date'] = user['creation_date']
            response.append(element)
            c += 1

        return json.dumps(response), OK

    def deleteUser(self, newsletter, mail):
        logger.info('delete user %s from newsletter %s',
                    mail, newsletter)
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        try:
            element_id = None
            count = 0
            for user in annotations:
                if user['email'] == mail:
                    element_id = count
                    break
                count += 1

            # elimino persona dalla newsletter
            if element_id is not None:
                annotations.pop(element_id)
            else:
                raise ValueError
        except ValueError:
            return MAIL_NOT_PRESENT

        return OK

    def deleteUserList(self, usersList, newsletter):
        # manca il modo di far capire se una mail non e presente nella lista
        logger.info('delete userslist %s from %s',
                    usersList, newsletter)
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        for user in usersList:
            try:
                element_id = None
                count = 0

                for u in annotations:
                    if u['email'] == user:
                        element_id = count
                        break
                    count += 1

                if element_id is not None:
                    annotations.pop(element_id)

            except ValueError:
                # to handle
                pass

        return OK

    def emptyNewsletterUsersList(self, newsletter):
        logger.info('DEBUG: emptyNewsletterUsersList %s', newsletter)
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        del annotations[:]

        return OK

    def unsubscribe(self, newsletter, mail):
        logger.info('DEBUG: unsubscribe %s %s', newsletter, mail)
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        try:
            element_id = None
            count = 0
            for user in annotations:
                if user['email'] == mail:
                    element_id = count
                    break
                count += 1

            # elimino persona dalla newsletter
            if element_id is not None:
                annotations.pop(element_id)
            else:
                raise ValueError

        except ValueError:
            return INEXISTENT_EMAIL

        return OK

    def addUser(self, newsletter, mail):
        logger.info('DEBUG: add user: %s %s', newsletter, mail)
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        if not mailValidation(mail):
            return INVALID_EMAIL

        # calculate new uuid for email
        generator = getUtility(IUUIDGenerator)
        uuid = generator()
        # controllo che la mail non sia gia presente e attiva nel db
        for user in annotations:
            if (
                (mail == user['email'] and user['is_active']) or
                (
                    mail == user['email'] and
                    not user['is_active'] and
                    isCreationDateExpired(user['creation_date'])
                )
            ):
                return ALREADY_SUBSCRIBED
        else:
            annotations.append(PersistentDict({
                'email': mail,
                'is_active': True,
                'token': uuid,
                'creation_date': datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            }))

        return OK

    def subscribe(self, newsletter, mail, name=None):
        logger.info('DEBUG: subscribe %s %s', newsletter, mail)
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER, None

        if not mailValidation(mail):
            return INVALID_EMAIL, None

        # calculate new uuid for email
        generator = getUtility(IUUIDGenerator)
        uuid = generator()
        for user in annotations:
            if (
                (mail == user['email'] and user['is_active']) or
                (
                    mail == user['email'] and
                    not user['is_active'] and
                    isCreationDateExpired(user['creation_date'])
                )
            ):
                return ALREADY_SUBSCRIBED, None
        else:
            annotations.append(PersistentDict({
                'email': mail,
                'is_active': False,
                'token': uuid,
                'creation_date': datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            }))

        return OK, uuid

    def sendMessage(self, newsletter, message):
        logger.debug('sendMessage %s %s', newsletter, message.title)
        nl = self._api(newsletter)
        annotations = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        # costruisco il messaggio
        body = u''
        body += nl.header.output if nl.header else u''
        body += u'<style>{css}</style>'.format(css=nl.css_style or u'')
        body += message.text.output if message.text else u''
        body += nl.footer.output if nl.footer else u''
        body = premailer.transform(body)
        try:
            # invio la mail ad ogni utente
            mail_host = api.portal.get_tool(name='MailHost')
            for user in annotations:
                mail_host.send(
                    body,
                    mto=user['email'],
                    mfrom=nl.sender_email,
                    subject=message.Title(),
                    charset='utf-8',
                    msg_type='text/html'
                )
        except SMTPRecipientsRefused:
            raise SMTPRecipientsRefused

        return OK
