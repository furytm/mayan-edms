from django.utils.translation import gettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(
    label=_(message='Government reference'), name='government_reference'
)

event_government_reference_generated = namespace.add_event_type(
    label=_(message='Government reference generated'),
    name='government_reference_generated'
)
