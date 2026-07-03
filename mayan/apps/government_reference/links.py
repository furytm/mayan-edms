from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.links import Link

from .icons import icon_government_reference_generate
from .permissions import permission_government_reference_generate

link_government_reference_generate = Link(
    args='resolved_object.id', icon=icon_government_reference_generate,
    permission=permission_government_reference_generate,
    text=_(message='Generate government reference'),
    view='government_reference:government_reference_generate'
)
