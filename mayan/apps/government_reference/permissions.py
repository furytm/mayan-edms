from django.utils.translation import gettext_lazy as _

from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_(message='Government reference'), name='government_reference'
)

permission_government_reference_generate = namespace.add_permission(
    label=_(message='Generate government reference number'),
    name='government_reference_generate'
)
