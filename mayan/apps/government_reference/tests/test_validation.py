from django.core.exceptions import ValidationError

from mayan.apps.testing.tests.base import BaseTestCase

from ..metadata_validators import GovernmentReferenceNumberValidator


class GovernmentReferenceNumberValidatorTestCase(BaseTestCase):
    def test_valid_reference_number(self):
        validator = GovernmentReferenceNumberValidator()

        validator.validate(input_data='MOF/PROC/2026/000001')

    def test_invalid_reference_number(self):
        validator = GovernmentReferenceNumberValidator()

        with self.assertRaises(expected_exception=ValidationError):
            validator.validate(input_data='MOF-PROC-2026-000001')
