# -*- coding: utf-8 -*-
from datetime import datetime
from email.utils import formataddr
from persistent.dict import PersistentDict
from plone import api
from rer.newsletter import logger
from rer.newsletter.behaviors.ships import IShippable
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
from rer.newsletter.utils import addToHistory
from rer.newsletter.utils import get_site_title
from smtplib import SMTPRecipientsRefused
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.interface import Interface

SUBSCRIBERS_KEY = 'rer.newsletter.subscribers'
HISTORY_KEY = 'rer.newsletter.channel.history'


class IChannelSender(Interface):
    """Marker interface to provide a Channel message sender"""


@implementer(IChannelSender)
class BaseAdapter(object):
    """ Adapter standard di base, invio sincrono usando plone
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    #  utils methods

    def get_annotations_for_channel(self, key, channel=None):
        if not channel:
            channel = self.context
        annotations = IAnnotations(channel)
        if key not in list(annotations.keys()):
            annotations[key] = PersistentDict({})
        return annotations[key]

    @property
    def active_subscriptions(self):
        subscribers = self.get_annotations_for_channel(key=SUBSCRIBERS_KEY)
        return len([x for x in subscribers.values() if x['is_active']])

    #  utils methods end

    def addChannel(self):
        logger.info('DEBUG: add channel {0}'.format(self.context.title))
        return OK

    def _getMessage(self, message, footer):
        logger.debug('getMessage %s %s', self.context.title, message.title)

        content = IShippable(message).message_content

        body = u''
        body += self.context.header.output if self.context.header else u''
        body += u'<style>{css}</style>'.format(
            css=self.context.css_style or u''
        )
        body += u'<div id="message_description"><p>{desc}</p></div>'.format(
            desc=message.description or u''
        )
        body += content
        body += self.context.footer.output if self.context.footer else u''
        body += footer or u''

        # passo la mail per il transform
        portal = api.portal.get()
        body = portal.portal_transforms.convertTo('text/mail', body)

        return body

    def set_start_send_infos(self, message):
        details = self.get_annotations_for_channel(key=HISTORY_KEY)
        subscribers = self.get_annotations_for_channel(key=SUBSCRIBERS_KEY)

        now = datetime.today().strftime('%d/%m/%Y %H:%M:%S')
        active_subscriptions = len(
            [x for x in subscribers.values() if x['is_active']]
        )
        details[self.context.title + str(len(list(details.keys())))] = {
            'num_active_subscribers': active_subscriptions,
            'send_date': now,
        }
        addToHistory(message, active_subscriptions)

    def prepare_body(self, message):
        unsubscribe_footer_template = self.context.restrictedTraverse(
            '@@unsubscribe_channel_template'
        )
        parameters = {
            'portal_name': get_site_title(),
            'channel_name': self.context.title,
            'unsubscribe_link': self.context.absolute_url() + '/@@unsubscribe',
        }
        footer = unsubscribe_footer_template(**parameters)
        return self._getMessage(message=message, footer=footer)

    def sendMessage(self, message):
        """ This is the primary method to send emails for the channel.
        """
        logger.debug('sendMessage %s %s', self.context.title, message.title)

        subscribers = self.get_annotations_for_channel(key=SUBSCRIBERS_KEY)

        nl_subject = (
            ' - ' + self.context.subject_email
            if self.context.subject_email
            else u''
        )
        sender = (
            self.context.sender_name
            and formataddr(  # noqa
                (self.context.sender_name, self.context.sender_email)
            )
            or self.context.sender_email  # noqa
        )
        subject = message.title + nl_subject

        self.set_start_send_infos(message=message)
        res = self.doSend(
            body=self.prepare_body(message=message),
            subject=subject,
            subscribers=subscribers,
            sender=sender,
        )
        return res

    def doSend(self, body, subject, subscribers, sender):
        """
        Override this method with a new (and more specific) adapter to
        customize the email sending.
        """
        mail_host = api.portal.get_tool(name='MailHost')
        try:
            for subscriber in subscribers.values():
                if subscriber['is_active']:
                    mail_host.send(
                        body.getData(),
                        mto=subscriber['email'],
                        mfrom=sender,
                        subject=subject,
                        charset='utf-8',
                        msg_type='text/html',
                    )
        except SMTPRecipientsRefused:
            return UNHANDLED

        return OK
