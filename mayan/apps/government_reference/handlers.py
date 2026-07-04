from django.core.exceptions import ValidationError

from mayan.apps.metadata.models.metadata_instance_models import DocumentMetadata

from .services import (
    DEFAULT_REFERENCE_DEPARTMENT, DEFAULT_REFERENCE_MINISTRY,
    generate_reference_number, get_government_reference_metadata_type
)


def handler_post_document_file_upload_generate_reference(
    instance, sender, **kwargs
):
    document = instance.document
    metadata_type = get_government_reference_metadata_type()

    if DocumentMetadata.objects.filter(
        document=document, metadata_type=metadata_type
    ).exists():
        return

    try:
        generate_reference_number(
            department=DEFAULT_REFERENCE_DEPARTMENT, document=document,
            ministry=DEFAULT_REFERENCE_MINISTRY
        )
    except ValidationError:
        if not DocumentMetadata.objects.filter(
            document=document, metadata_type=metadata_type
        ).exists():
            raise
