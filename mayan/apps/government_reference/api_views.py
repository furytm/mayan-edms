from mayan.apps.rest_api import generics

from .permissions import permission_government_reference_generate
from .serializers import GovernmentReferenceGenerateSerializer


class APIGovernmentReferenceGenerateView(generics.CreateAPIView):
    """
    post: Generate a government reference number for a document.
    """
    mayan_view_permission_map = {
        'POST': permission_government_reference_generate
    }
    serializer_class = GovernmentReferenceGenerateSerializer
