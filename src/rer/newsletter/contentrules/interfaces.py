# -*- coding: utf-8 -*-
from rer.newsletter import _
from zope import schema
from zope.interface import Interface


# class INotifyOnSubscribe(Interface):
#     source = schema.TextLine(
#         title=_(u'Sender email'),
#         description=_(u'The email address that sends the email. If no email is \
#             provided here, it will use the portal from address.'),
#         required=False
#     )
#
#     dest_addr = schema.TextLine(
#         title=_(u'Receiver email'),
#         description=_(
#             u'The address where you want to send the e-mail message.'),
#         required=True
#     )
#
#
# class INotifyOnUnsubscribe(Interface):
#     source = schema.TextLine(
#         title=_(u'Sender email'),
#         description=_(u'The email address that sends the email. If no email is \
#             provided here, it will use the portal from address.'),
#         required=False
#     )
#
#     dest_addr = schema.TextLine(
#         title=_(u'Receiver email'),
#         description=_(
#             'The address where you want to send the e-mail message.'),
#         required=True
#     )
