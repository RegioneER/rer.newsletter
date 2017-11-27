# -*- coding: utf-8 -*-
import json
import re
import uuid
from datetime import datetime, timedelta
from smtplib import SMTPRecipientsRefused

from rer.newsletter import _, logger
from rer.newsletter.utility.newsletter import (ALREADY_ACTIVE,
                                               ALREADY_SUBSCRIBED, FILE_FORMAT,
                                               INEXISTENT_EMAIL, INVALID_EMAIL,
                                               INVALID_NEWSLETTER,
                                               INVALID_SECRET,
                                               MAIL_NOT_PRESENT,
                                               NEWSLETTER_USED, OK,
                                               PROBLEM_WITH_MAIL,
                                               INewsletterUtility)

import premailer
from persistent.dict import PersistentDict
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.interface import Invalid, implementer

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


# da fixare la validazione
def uuidValidation(uuid_string):
    try:
        uuid.UUID(uuid_string, version=4)
    except ValueError:
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
                # annotations[KEY] = PersistentList([])
                annotations[KEY] = PersistentDict({})
            return annotations[KEY], obj

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
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER, None

        # valido il secret
        if not uuidValidation(secret):
            return INVALID_SECRET, None

        # attivo l'utente
        count = 0
        for user in annotations:
            if annotations[user]['token'] == secret:
                if annotations[user]['is_active']:
                    return ALREADY_ACTIVE, user
                else:
                    element_id = user
                    break
            count += 1

        if element_id is not None:
            # riscrivo l'utente mettendolo a attivo
            annotations[element_id] = {
                'email': element_id,
                'is_active': True,
                'token': annotations[element_id]['token'],
                'creation_date': annotations[element_id]['creation_date'],
            }

            return OK, element_id
        else:
            return INVALID_SECRET, element_id

    def importUsersList(self, usersList, newsletter):
        logger.info('DEBUG: import userslist in %s', newsletter)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        for user in usersList:
            match = re.match(
                '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]' +
                '+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                user
            )
            if match is not None:
                annotations[user] = {
                    'email': user,
                    'is_active': True,
                    'token': unicode(uuid.uuid4()),
                    'creation_date': datetime.today().strftime(
                        '%d/%m/%Y %H:%M:%S'
                    ),
                }
            else:
                logger.info('INVALID_EMAIL: %s', user)

        return OK

    def exportUsersList(self, newsletter):
        logger.info('DEBUG: export users of newsletter: %s', newsletter)
        response = []
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        c = 0
        for user in annotations.keys():
            element = {}
            element['id'] = c
            element['email'] = annotations[user]['email']
            element['is_active'] = annotations[user]['is_active']
            element['creation_date'] = annotations[user]['creation_date']
            response.append(element)
            c += 1

        return json.dumps(response), OK

    def deleteUser(self, newsletter, mail=None, secret=None):
        logger.info('delete user %s from newsletter %s',
                    mail, newsletter)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER, None

        if secret is not None:
            # cancello l'utente con il secret (AnonimousUser)

            # valido il secret
            if not uuidValidation(secret):
                return INVALID_SECRET, None

            for user in annotations:
                if annotations[user]['token'] == unicode(secret):
                    cd = annotations[user]['creation_date']
                    if isCreationDateExpired(cd):
                        del annotations[user]
                        return OK, user
                    else:
                        return INVALID_SECRET, user

            return MAIL_NOT_PRESENT, None

        else:
            # cancello l'utente con la mail (Admin)
            try:
                if mail in annotations.keys():
                    del annotations[mail]
                    return OK
                else:
                    raise ValueError
            except ValueError:
                return MAIL_NOT_PRESENT

    def deleteUserList(self, usersList, newsletter):
        # manca il modo di far capire se una mail non e presente nella lista
        logger.info('delete userslist from %s', newsletter)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        for user in usersList:
            try:

                if user in annotations.keys():
                    del annotations[user]

            except ValueError:
                # to handle
                pass

        return OK

    def emptyNewsletterUsersList(self, newsletter):
        logger.info('DEBUG: emptyNewsletterUsersList %s', newsletter)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        annotations.clear()

        return OK

    def unsubscribe(self, newsletter, user):
        logger.info('DEBUG: unsubscribe %s %s', newsletter, user)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER, None

        try:
            secret = unicode(uuid.uuid4())

            if user in annotations.keys():
                annotations[user] = {
                    'email': user,
                    'is_active': True,
                    'token': secret,
                    'creation_date': datetime.today().strftime(
                        '%d/%m/%Y %H:%M:%S'
                    ),
                }
            else:
                raise ValueError

        except ValueError:
            return INEXISTENT_EMAIL, None

        return OK, secret

    def addUser(self, newsletter, mail):
        logger.info('DEBUG: add user: %s %s', newsletter, mail)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        if not mailValidation(mail):
            return INVALID_EMAIL

        # controllo che la mail non sia gia presente e attiva nel db
        for user in annotations.keys():
            if (
                (
                    mail == annotations[user]['email'] and
                    annotations[user]['is_active']
                ) or
                (
                    mail == annotations[user]['email'] and
                    not annotations[user]['is_active'] and
                    isCreationDateExpired(annotations[user]['creation_date'])
                )
            ):
                return ALREADY_SUBSCRIBED
        else:
            annotations[mail] = {
                'email': mail,
                'is_active': True,
                'token': unicode(uuid.uuid4()),
                'creation_date': datetime.today().strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
            }

        return OK

    def subscribe(self, newsletter, mail, name=None):
        logger.info('DEBUG: subscribe %s %s', newsletter, mail)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER, None

        if not mailValidation(mail):
            return INVALID_EMAIL, None

        uuid_activation = unicode(uuid.uuid4())
        for user in annotations.keys():
            if (
                (
                    mail == annotations[user]['email'] and
                    annotations[user]['is_active']
                ) or
                (
                    mail == annotations[user]['email'] and
                    not annotations[user]['is_active'] and
                    isCreationDateExpired(annotations[user]['creation_date'])
                )
            ):
                return ALREADY_SUBSCRIBED, None
        else:
            annotations[mail] = {
                'email': mail,
                'is_active': False,
                'token': uuid_activation,
                'creation_date': datetime.today().strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
            }

        return OK, uuid_activation

    def getMessage(self, newsletter, message):
        logger.debug('getMessage %s %s', newsletter, message.title)

        body = u''
        body += newsletter.header.output if newsletter.header else u''
        body += u'<style>{css}</style>'.format(css=newsletter.css_style or u'')
        body += message.text.output if message.text else u''
        body += newsletter.footer.output if newsletter.footer else u''
        body = premailer.transform(body)

        return body

    def sendMessage(self, newsletter, message):
        logger.debug('sendMessage %s %s', newsletter, message.title)
        nl = self._api(newsletter)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return INVALID_NEWSLETTER

        # costruisco il messaggio
        body = self.getMessage(nl, message)

        try:
            # invio la mail ad ogni utente
            mail_host = api.portal.get_tool(name='MailHost')
            for user in annotations.keys():
                if annotations[user]['is_active']:
                    mail_host.send(
                        body,
                        mto=annotations[user]['email'],
                        mfrom=nl.sender_email,
                        subject=message.Title(),
                        charset='utf-8',
                        msg_type='text/html'
                    )
        except SMTPRecipientsRefused:
            raise SMTPRecipientsRefused

        return OK

    def getNumActiveSubscribers(self, newsletter):
        logger.debug('Get number of active subscribers from %s', newsletter)
        annotations, newsletter_obj = self._storage(newsletter)
        if annotations is None:
            return None, INVALID_NEWSLETTER

        count = 0
        for user in annotations.keys():
            if annotations[user]['is_active']:
                count += 1

        return count, OK

    def getErrorMessage(self, code_error):

        if code_error == OK:
            return _(u'generic_success_message', default=u'everything ok.')
        elif code_error == INVALID_EMAIL:
            return _(u'invalid_email_message', default=u'Invalid Email.')
        elif code_error == ALREADY_SUBSCRIBED:
            return _(
                u'already_subscribed_message',
                default=u'Email already subscribed.'
            )
        elif code_error == INEXISTENT_EMAIL:
            return _(u'inexistent_email_message', default=u'Inexistent email.')
        elif code_error == ALREADY_ACTIVE:
            return _(
                u'already_active_message',
                default=u'Email already activated.'
            )
        elif code_error == INVALID_NEWSLETTER:
            return _(
                u'invalid_newsletter_message',
                default=u'Invalid newsletter.'
            )
        elif code_error == INVALID_SECRET:
            return _(u'invalid_secret_message', default=u'Invalid secret.')
        elif code_error == MAIL_NOT_PRESENT:
            return _(u'mail_not_present_message', default=u'Mail not present.')
        elif code_error == NEWSLETTER_USED:
            return _(
                u'newsletter_used_message',
                default=u'Newsletter already used.'
            )
        elif code_error == FILE_FORMAT:
            return _(
                u'file_format_message',
                default=u'Wrong file format.'
            )
        elif code_error == PROBLEM_WITH_MAIL:
            return _(
                u'problem_with_email',
                default=u'Problema with email.'
            )
        else:
            return _(u'unhandled_error_message', default=u'Unhandled error.')
