from django.apps import apps
from django.utils.translation import gettext_lazy as _

from mayan.apps.app_manager.apps import MayanAppConfig
from mayan.apps.common.menus import menu_object
from mayan.apps.events.classes import ModelEventType
from mayan.apps.acls.classes import ModelPermission
from mayan.apps.documents.signals import signal_post_document_file_upload

from .events import event_government_reference_generated
from .links import link_government_reference_generate
from .permissions import permission_government_reference_generate


class GovernmentReferenceApp(MayanAppConfig):
    app_namespace = 'government_reference'
    app_url = 'government_reference'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.government_reference'
    verbose_name = _(message='Government reference')

    def ready(self):
        super().ready()

        from .handlers import handler_post_document_file_upload_generate_reference
        from .wizard_steps import patch_document_create_metadata_wizard_step

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        ModelEventType.register(
            model=Document, event_types=(event_government_reference_generated,)
        )
        ModelPermission.register(
            model=Document,
            permissions=(permission_government_reference_generate,)
        )
        menu_object.bind_links(
            links=(link_government_reference_generate,), sources=(Document,)
        )
        signal_post_document_file_upload.connect(
            dispatch_uid='government_reference_handler_post_document_file_upload_generate_reference',
            receiver=handler_post_document_file_upload_generate_reference,
            sender=apps.get_model(
                app_label='documents', model_name='DocumentFile'
            )
        )
        patch_document_create_metadata_wizard_step()
