# -*- coding: utf-8 -*-
from plone import api
from plone import schema
from plone.protect.authenticator import createToken
from plone.z3cform.layout import wrap_form
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import SUBSCRIBED
from rer.newsletter.utility.channel import UNHANDLED
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from zope.interface import Interface


class ISubscribeForm(Interface):
    """ define field for channel subscription """
    email = schema.Email(
        title=_(u'subscribe_user', default=u'Subscription Mail'),
        description=_(
            u'subscribe_user_description',
            default=u'Mail for subscribe to a channel'
        ),
        required=True,
    )


class SubscribeForm(form.Form):

    ignoreContext = True
    fields = field.Fields(ISubscribeForm)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        add_bundle_on_request(self.request, 'unsubscribe')

    def isVisible(self):
        if self.context.is_subscribable:
            return True
        else:
            return False

    @button.buttonAndHandler(u'subscribe')
    def handleSave(self, action):
        status = UNHANDLED
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        email = None
        if self.context.portal_type == 'Channel':
            channel = self.context.id_channel
        email = data['email']

        if self.context.is_subscribable:
            api_channel = getUtility(IChannelUtility)
            status, secret = api_channel.subscribe(channel, email)

        if status == SUBSCRIBED:

            # creo il token CSRF
            token = createToken()

            # mando mail di conferma
            url = self.context.absolute_url()
            url += '/confirmaction?secret=' + secret
            url += '&_authenticator=' + token
            url += '&action=subscribe'

            mail_template = self.context.restrictedTraverse(
                '@@activeuser_template'
            )

            parameters = {
                'header': self.context.header,
                'footer': self.context.footer,
                'style': self.context.css_style,
                'activationUrl': url
            }

            mail_text = mail_template(**parameters)

            portal = api.portal.get()
            mail_text = portal.portal_transforms.convertTo(
                'text/mail', mail_text)

            mailHost = api.portal.get_tool(name='MailHost')
            mailHost.send(
                mail_text.getData(),
                mto=email,
                mfrom='noreply@rer.it',
                subject='Email di attivazione',
                charset='utf-8',
                msg_type='text/html',
                immediate=True
            )

            api.portal.show_message(
                message=_(
                    u'status_user_subscribed',
                    default=u'Utente iscritto. Mail di conferma inviata.'
                ),
                request=self.request,
                type=u'info'
            )

        else:
            if status == 2:
                logger.exception(
                    'user already subscribed'
                )
                api.portal.show_message(
                    message=_(u'user_already_subscribed',
                              default=u'User already subscribed.'),
                    request=self.request,
                    type=u'error'
                )
            else:
                logger.exception(
                    'unhandled error subscribe user'
                )
                api.portal.show_message(
                    message=u'Problems...{0}'.format(status),
                    request=self.request,
                    type=u'error'
                )


subscribe_view = wrap_form(
    SubscribeForm,
    index=ViewPageTemplateFile('templates/subscribechannel.pt')
)
