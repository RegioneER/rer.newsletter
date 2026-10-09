# -*- coding: utf-8 -*-
from plone import schema
from plone.app.registry.browser import controlpanel
from rer.newsletter import _
from zope.interface import Interface
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def checkExpiredTimeToken(value):
    if value > 0:
        return True


class ISettingsSchema(Interface):
    """Schema for channel settings"""

    source_link = schema.TextLine(
        title=_("source_link", default="Link sorgente"),
        description=_("description_source_link", default="Indirizzo da sostituire"),
        default="",
        required=False,
    )

    destination_link = schema.TextLine(
        title=_("destination_link", default="Link di destinazione"),
        description=_(
            "description_destination_link",
            default="Indirizzo da sostituire. Se plone.volto è installato e il frontend_domain configurato, questo valore è ignorato.",
        ),
        required=False,
    )

    expired_time_token = schema.Int(
        title=_("expired_time_token", default="Validità del token in ore"),
        required=False,
        default=48,
        # constraint=checkExpiredTimeToken,
    )

    matomo_tracking_enabled = schema.Bool(
        title=_(
            "matomo_tracking_enabled",
            default="Aggiungi parametri di tracciamento Matomo ai link",
        ),
        description=_(
            "description_matomo_tracking_enabled",
            default="Se selezionato, ai link verso il portale presenti nei "
            "messaggi inviati vengono aggiunti i parametri mtm_campaign, "
            "mtm_source, mtm_medium e mtm_content. Funziona solo se "
            "l'istanza ha la variabile d'ambiente MATOMO_SITE_ID valorizzata.",
        ),
        default=True,
        required=False,
    )

    matomo_content_param = schema.Choice(
        title=_("matomo_content_param", default="Valore di mtm_content"),
        description=_(
            "description_matomo_content_param",
            default="Cosa usare come valore del parametro mtm_content per il "
            "contenuto linkato.",
        ),
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm(
                    value="id", title=_("matomo_content_id", default="Nome breve")
                ),
                SimpleTerm(
                    value="portal_type",
                    title=_("matomo_content_portal_type", default="Tipo di contenuto"),
                ),
            ]
        ),
        default="id",
        required=False,
    )


class ChannelSettings(controlpanel.RegistryEditForm):
    schema = ISettingsSchema
    id = "ChannelSettings"
    label = _("channel_setting", default="Channel Settings")

    def updateFields(self):
        super(ChannelSettings, self).updateFields()

    def updateWidgets(self):
        super(ChannelSettings, self).updateWidgets()


class ChannelSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ChannelSettings
