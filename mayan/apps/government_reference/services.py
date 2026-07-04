from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from mayan.apps.metadata.models.document_type_metadata_type_models import (
    DocumentTypeMetadataType
)
from mayan.apps.metadata.models.metadata_instance_models import DocumentMetadata
from mayan.apps.metadata.models.metadata_type_models import MetadataType

from .events import event_government_reference_generated
from .models import GovernmentReferenceSequence

GOVERNMENT_REFERENCE_METADATA_LABEL = 'Government Reference Number'
GOVERNMENT_REFERENCE_METADATA_NAME = 'government_reference_number'
GOVERNMENT_REFERENCE_VALIDATOR_PATH = (
    'mayan.apps.government_reference.metadata_validators.'
    'GovernmentReferenceNumberValidator'
)
DEFAULT_REFERENCE_DEPARTMENT = 'PROC'
DEFAULT_REFERENCE_MINISTRY = 'MOF'


def get_government_reference_metadata_type():
    metadata_type, created = MetadataType.objects.get_or_create(
        name=GOVERNMENT_REFERENCE_METADATA_NAME,
        defaults={
            'label': GOVERNMENT_REFERENCE_METADATA_LABEL,
            'validation': GOVERNMENT_REFERENCE_VALIDATOR_PATH
        }
    )

    if not created and not metadata_type.validation:
        metadata_type.validation = GOVERNMENT_REFERENCE_VALIDATOR_PATH
        metadata_type.save(update_fields=('validation',))

    return metadata_type


def generate_reference_number(document, ministry, department, user=None):
    """
    Generate the next government reference number for a ministry,
    department, and year sequence, then store it as document metadata.
    """
    year = timezone.now().year
    ministry = ministry.strip().upper()
    department = department.strip().upper()

    with transaction.atomic():
        metadata_type = get_government_reference_metadata_type()

        DocumentTypeMetadataType.objects.get_or_create(
            document_type=document.document_type, metadata_type=metadata_type
        )

        if DocumentMetadata.objects.filter(
            document=document, metadata_type=metadata_type
        ).exists():
            raise ValidationError(
                message='Document already has a government reference number.'
            )

        try:
            sequence = GovernmentReferenceSequence.objects.select_for_update().get(
                department=department, ministry=ministry, year=year
            )
        except GovernmentReferenceSequence.DoesNotExist:
            try:
                with transaction.atomic():
                    sequence = GovernmentReferenceSequence.objects.create(
                        department=department, ministry=ministry, year=year
                    )
            except IntegrityError:
                sequence = GovernmentReferenceSequence.objects.select_for_update().get(
                    department=department, ministry=ministry, year=year
                )

        sequence.last_sequence += 1
        sequence.save(update_fields=('last_sequence', 'updated_at'))

        reference_number = '{ministry}/{department}/{year}/{sequence:06d}'.format(
            department=department, ministry=ministry,
            sequence=sequence.last_sequence, year=year
        )

        if DocumentMetadata.objects.filter(
            metadata_type=metadata_type, value=reference_number
        ).exists():
            raise ValidationError(
                message='Government reference number already exists.'
            )

        document_metadata = DocumentMetadata(
            document=document, metadata_type=metadata_type,
            value=reference_number
        )
        document_metadata.full_clean()
        document_metadata.save()

        event_government_reference_generated.commit(
            action_object=document_metadata, actor=user, target=document
        )

    return reference_number
