from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from django.core.exceptions import ValidationError

from mayan.apps.documents.tests.base import (
    GenericDocumentTestCase, GenericTransactionDocumentTestCase
)
from mayan.apps.metadata.models.document_type_metadata_type_models import (
    DocumentTypeMetadataType
)
from mayan.apps.metadata.models.metadata_instance_models import DocumentMetadata
from mayan.apps.metadata.models.metadata_type_models import MetadataType
from mayan.apps.metadata.permissions import permission_document_metadata_add
from mayan.apps.metadata.wizard_steps import DocumentCreateWizardStepMetadata

from ..handlers import handler_post_document_file_upload_generate_reference
from ..models import GovernmentReferenceSequence
from ..services import (
    DEFAULT_REFERENCE_DEPARTMENT, DEFAULT_REFERENCE_MINISTRY,
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

    def test_post_document_file_upload_handler_generates_reference_number(self):
        handler_post_document_file_upload_generate_reference(
            instance=SimpleNamespace(document=self._test_document), sender=None
        )

        metadata_type = get_government_reference_metadata_type()
        document_metadata = DocumentMetadata.objects.get(
            document=self._test_document, metadata_type=metadata_type
        )

        self.assertRegex(
            text=document_metadata.value,
            expected_regex=r'^%s/%s/\d{4}/000001$' % (
                DEFAULT_REFERENCE_MINISTRY, DEFAULT_REFERENCE_DEPARTMENT
            )
        )

    def test_post_document_file_upload_handler_is_idempotent(self):
        handler_post_document_file_upload_generate_reference(
            instance=SimpleNamespace(document=self._test_document), sender=None
        )
        handler_post_document_file_upload_generate_reference(
            instance=SimpleNamespace(document=self._test_document), sender=None
        )

        metadata_type = get_government_reference_metadata_type()

        self.assertEqual(
            DocumentMetadata.objects.filter(
                document=self._test_document, metadata_type=metadata_type
            ).count(), 1
        )
        self.assertEqual(
            GovernmentReferenceSequence.objects.get(
                department=DEFAULT_REFERENCE_DEPARTMENT,
                ministry=DEFAULT_REFERENCE_MINISTRY
            ).last_sequence, 1
        )

    def test_upload_metadata_queryset_excludes_reference_number(self):
        metadata_type = get_government_reference_metadata_type()
        test_metadata_type = MetadataType.objects.create(
            name='test_metadata_type', label='Test metadata type'
        )

        DocumentTypeMetadataType.objects.create(
            document_type=self._test_document_type,
            metadata_type=metadata_type
        )
        DocumentTypeMetadataType.objects.create(
            document_type=self._test_document_type,
            metadata_type=test_metadata_type
        )

        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_metadata_add
        )
        self.grant_access(
            obj=metadata_type, permission=permission_document_metadata_add
        )
        self.grant_access(
            obj=test_metadata_type,
            permission=permission_document_metadata_add
        )

        queryset = DocumentCreateWizardStepMetadata.get_metadata_queryset_for_document_type(
            document_type=self._test_document_type, user=self._test_case_user
        )

        self.assertNotIn(metadata_type, queryset)
        self.assertIn(test_metadata_type, queryset)


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
