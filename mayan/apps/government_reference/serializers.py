from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError

from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.rest_api import serializers
from mayan.apps.rest_api.relations import FilteredPrimaryKeyRelatedField

from .services import generate_reference_number


class GovernmentReferenceGenerateSerializer(serializers.Serializer):
    document_id = FilteredPrimaryKeyRelatedField(
        help_text=_(message='Primary key of the document.'),
        label=_(message='Document ID'), source='document',
        source_permission=permission_document_view,
        source_queryset=Document.valid.all(), write_only=True
    )
    ministry = serializers.CharField(
        label=_(message='Ministry'), max_length=16, write_only=True
    )
    department = serializers.CharField(
        label=_(message='Department'), max_length=32, write_only=True
    )
    reference_number = serializers.CharField(
        label=_(message='Reference number'), read_only=True
    )

    def create(self, validated_data):
        try:
            reference_number = generate_reference_number(
                document=validated_data['document'],
                department=validated_data['department'],
                ministry=validated_data['ministry'],
                user=self.context['request'].user
            )
        except DjangoValidationError as exception:
            raise ValidationError(detail=exception.messages) from exception

        return {'reference_number': reference_number}
