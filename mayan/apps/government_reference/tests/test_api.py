from rest_framework import status

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.mixins.document_mixins import (
    DocumentTestMixin
)
from mayan.apps.metadata.models.metadata_instance_models import DocumentMetadata
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..permissions import permission_government_reference_generate
from ..services import get_government_reference_metadata_type


class GovernmentReferenceAPITestCase(DocumentTestMixin, BaseAPITestCase):
    auto_create_test_document_stub = True
    auto_upload_test_document = False

    def _request_government_reference_generate_api_view(self):
        return self.post(
            viewname='rest_api:government-reference-generate',
            data={
                'department': 'PROC',
                'document_id': self._test_document.pk,
                'ministry': 'MOF'
            }
        )

    def test_generate_reference_api_view_no_permission(self):
        response = self._request_government_reference_generate_api_view()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_reference_api_view_with_access(self):
        self.grant_access(
            obj=self._test_document, permission=permission_document_view
        )
        self.grant_access(
            obj=self._test_document,
            permission=permission_government_reference_generate
        )

        response = self._request_government_reference_generate_api_view()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertRegex(
            text=response.data['reference_number'],
            expected_regex=r'^MOF/PROC/\d{4}/000001$'
        )

        metadata_type = get_government_reference_metadata_type()
        self.assertTrue(
            DocumentMetadata.objects.filter(
                document=self._test_document, metadata_type=metadata_type,
                value=response.data['reference_number']
            ).exists()
        )
