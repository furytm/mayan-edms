from django.utils.translation import gettext_lazy as _

from mayan.apps.documents.models.document_models import Document
from mayan.apps.views.exceptions import ActionError
from mayan.apps.views.generics import MultipleObjectFormActionView

from .forms import GovernmentReferenceGenerateForm
from .icons import icon_government_reference_generate
from .permissions import permission_government_reference_generate
from .services import generate_reference_number


class GovernmentReferenceGenerateView(MultipleObjectFormActionView):
    form_class = GovernmentReferenceGenerateForm
    object_permission = permission_government_reference_generate
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid.all()
    success_message_single = _(
        message='Government reference generated for document: %(object)s.'
    )
    view_icon = icon_government_reference_generate

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _(message='Generate government reference for: %s') % self.object
        }

    def object_action(self, form, instance):
        try:
            generate_reference_number(
                document=instance,
                department=form.cleaned_data['department'],
                ministry=form.cleaned_data['ministry'], user=self.request.user
            )
        except Exception as exception:
            raise ActionError(exception) from exception
