import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from mayan.apps.metadata.classes import MetadataValidator


class GovernmentReferenceNumberValidator(MetadataValidator):
    label = _(message='Government reference number validator')

    def execute(self, input_data):
        result = re.fullmatch(
            pattern=r'[A-Z0-9]{2,16}/[A-Z0-9]{2,32}/\d{4}/\d{6}',
            string=input_data or ''
        )

        if not result:
            raise ValidationError(
                message=_(
                    message='Enter a valid government reference number in '
                    'MINISTRY/DEPARTMENT/YEAR/SEQUENCE format.'
                )
            )
