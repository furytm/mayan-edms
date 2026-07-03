from django.utils.translation import gettext_lazy as _

from mayan.apps.forms import form_fields, forms


class GovernmentReferenceGenerateForm(forms.Form):
    ministry = form_fields.CharField(
        help_text=_(message='Ministry abbreviation. Example: MOF.'),
        label=_(message='Ministry'), max_length=16
    )
    department = form_fields.CharField(
        help_text=_(message='Department abbreviation. Example: PROC.'),
        label=_(message='Department'), max_length=32
    )
