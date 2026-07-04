from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from mayan.apps.metadata.models.metadata_type_models import MetadataType
from mayan.apps.metadata.wizard_steps import DocumentCreateWizardStepMetadata
from mayan.apps.sources.wizard_steps import DocumentCreateWizardStepDocumentType

from .services import GOVERNMENT_REFERENCE_METADATA_NAME


def _exclude_government_reference_metadata(queryset):
    return queryset.exclude(name=GOVERNMENT_REFERENCE_METADATA_NAME)


def patch_document_create_metadata_wizard_step():
    if getattr(
        DocumentCreateWizardStepMetadata,
        '_government_reference_patch_applied', False
    ):
        return

    original_get_metadata_queryset_for_document = (
        DocumentCreateWizardStepMetadata.get_metadata_queryset_for_document
    )
    original_get_metadata_queryset_for_document_type = (
        DocumentCreateWizardStepMetadata.get_metadata_queryset_for_document_type
    )

    @staticmethod
    def get_metadata_queryset_for_document(document, user=None):
        queryset = original_get_metadata_queryset_for_document(
            document=document, user=user
        )
        return _exclude_government_reference_metadata(queryset=queryset)

    @staticmethod
    def get_metadata_queryset_for_document_type(document_type, user):
        queryset = original_get_metadata_queryset_for_document_type(
            document_type=document_type, user=user
        )
        return _exclude_government_reference_metadata(queryset=queryset)

    @classmethod
    def condition(cls, wizard):
        cleaned_data = wizard.get_cleaned_data_for_step(
            step=DocumentCreateWizardStepDocumentType.name
        ) or {}
        document_type = cleaned_data.get('document_type')

        if document_type:
            return cls.get_metadata_queryset_for_document_type(
                document_type=document_type, user=wizard.request.user
            ).exists()

    @classmethod
    def get_next_is_enabled(cls, wizard):
        step_data = wizard.get_cleaned_data_for_step(
            step=DocumentCreateWizardStepDocumentType.name
        )
        user = wizard.request.user

        if step_data:
            document_type = step_data['document_type']

            queryset_metadata_types = cls.get_metadata_queryset_for_document_type(
                document_type=document_type, user=user
            )
            queryset_metadata_types_required = MetadataType.objects.get_for_document_type(
                document_type=document_type, required=True
            )
            queryset_metadata_types_required = _exclude_government_reference_metadata(
                queryset=queryset_metadata_types_required
            )

            has_required_metadata = not queryset_metadata_types_required.exclude(
                pk__in=queryset_metadata_types.values('pk')
            ).exists()

            if not has_required_metadata:
                messages.error(
                    message=_(
                        message='One of more metadata types that are '
                        'required for this document type are not available.'
                    ), request=wizard.request
                )
                wizard.render_goto_step(goto_step=0)

                return False

        return True

    DocumentCreateWizardStepMetadata.get_metadata_queryset_for_document = (
        get_metadata_queryset_for_document
    )
    DocumentCreateWizardStepMetadata.get_metadata_queryset_for_document_type = (
        get_metadata_queryset_for_document_type
    )
    DocumentCreateWizardStepMetadata.condition = condition
    DocumentCreateWizardStepMetadata.get_next_is_enabled = get_next_is_enabled
    DocumentCreateWizardStepMetadata._government_reference_patch_applied = True
