from concurrent.futures import ThreadPoolExecutor

from django.core.exceptions import ValidationError

from mayan.apps.documents.tests.base import (
    GenericDocumentTestCase, GenericTransactionDocumentTestCase
)
from mayan.apps.metadata.models.metadata_instance_models import DocumentMetadata

from ..models import GovernmentReferenceSequence
from ..services import (
    GOVERNMENT_REFERENCE_METADATA_NAME, generate_reference_number,
    get_government_reference_metadata_type
)


class GovernmentReferenceServiceTestCase(GenericDocumentTestCase):
    auto_create_test_document_stub = True
    auto_upload_test_document = False

    def test_generate_reference_number(self):
        reference_number = generate_reference_number(
            document=self._test_document, department='PROC', ministry='MOF'
        )

        self.assertRegex(
            text=reference_number, expected_regex=r'^MOF/PROC/\d{4}/000001$'
        )

        sequence = GovernmentReferenceSequence.objects.get(
            department='PROC', ministry='MOF'
        )
        self.assertEqual(sequence.last_sequence, 1)

    def test_generate_reference_number_creates_metadata(self):
        reference_number = generate_reference_number(
            document=self._test_document, department='PROC', ministry='MOF'
        )

        metadata_type = get_government_reference_metadata_type()
        document_metadata = DocumentMetadata.objects.get(
            document=self._test_document, metadata_type=metadata_type
        )

        self.assertEqual(document_metadata.value, reference_number)
        self.assertEqual(
            document_metadata.metadata_type.name,
            GOVERNMENT_REFERENCE_METADATA_NAME
        )

    def test_generate_reference_number_duplicate_document(self):
        generate_reference_number(
            document=self._test_document, department='PROC', ministry='MOF'
        )

        with self.assertRaises(expected_exception=ValidationError):
            generate_reference_number(
                document=self._test_document, department='PROC',
                ministry='MOF'
            )


class GovernmentReferenceConcurrencyTestCase(
    GenericTransactionDocumentTestCase
):
    auto_create_test_document_stub = True
    auto_upload_test_document = False
    _test_document_count = 2

    def test_concurrent_generation_returns_unique_numbers(self):
        def generate(document_id):
            document = self._test_document_list[document_id]
            return generate_reference_number(
                document=document, department='PROC', ministry='MOF'
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            reference_numbers = list(executor.map(generate, (0, 1)))

        self.assertEqual(len(set(reference_numbers)), 2)
        self.assertEqual(
            sorted(reference_numbers)[0][-6:], '000001'
        )
        self.assertEqual(
            sorted(reference_numbers)[1][-6:], '000002'
        )
