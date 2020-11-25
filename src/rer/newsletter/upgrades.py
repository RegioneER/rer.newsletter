# -*- coding: utf-8 -*-
from plone import api
from rer.newsletter import logger
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from plone.app.layout.viewlets.content import ContentHistoryView

import re


default_profile = "profile-rer.newsletter:default"

KEY = "rer.newsletter.channel.history"


def migrate_to_1001(context):
    setup_tool = api.portal.get_tool("portal_setup")
    setup_tool.runImportStepFromProfile(default_profile, "plone.app.registry")
    logger.info(u"Updated to 1001")


def migrate_to_1002(context):
    setup_tool = api.portal.get_tool("portal_setup")
    setup_tool.runImportStepFromProfile(default_profile, "typeinfo")
    setup_tool.runImportStepFromProfile(default_profile, "workflow")
    logger.info(u"Updated to 1002")


def migrate_to_1003(context):
    setup_tool = api.portal.get_tool("portal_setup")
    setup_tool.runImportStepFromProfile(default_profile, "typeinfo")
    logger.info(u"Updated to 1003")


def migrate_to_1004(context):
    """
    Fix channel send history
    """
    for channel_brain in api.content.find(portal_type="Channel"):
        channel = channel_brain.getObject()
        channel_annotations = IAnnotations(channel)
        channel_annotations[KEY] = PersistentList()
        new_history = []
        messages = api.content.find(
            context=channel, portal_type=["Message", "Shippable Collection"]
        )
        for brain in messages:
            item = brain.getObject()
            send_history = extract_send_history(item)
            for action in send_history:
                uid = "{time}-{id}".format(
                    time=action["time"].strftime("%Y%m%d%H%M%S"),
                    id=item.getId(),
                )
                subscribers = int(
                    re.search(
                        r"Inviato il messaggio a (.*?) utenti.",
                        action["comments"],
                    ).group(1)
                )
                new_history.append(
                    PersistentDict(
                        {
                            "uid": uid,
                            "message": item.title,
                            "subscribers": subscribers,
                            "send_date_start": action["time"].strftime(
                                "%d/%m/%Y %H:%M:%S"
                            ),
                            "send_date_end": action["time"].strftime(
                                "%d/%m/%Y %H:%M:%S"
                            ),
                            "completed": True,
                        }
                    )
                )
            item_annotations = IAnnotations(item)
            if "rer.newsletter.message.details" in item_annotations:
                del item_annotations["rer.newsletter.message.details"]
        channel_annotations[KEY].extend(
            sorted(new_history, key=lambda i: i.get("uid", ""))
        )


def extract_send_history(item):
    history = ContentHistoryView(item, item.REQUEST).fullHistory()
    return [x for x in history if x["action"] == "Invio"]
