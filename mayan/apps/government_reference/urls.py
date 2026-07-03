from django.urls import re_path

from .api_views import APIGovernmentReferenceGenerateView
from .views import GovernmentReferenceGenerateView

urlpatterns = [
    re_path(
        route=r'^documents/(?P<document_id>\d+)/government_reference/generate/$',
        name='government_reference_generate',
        view=GovernmentReferenceGenerateView.as_view()
    )
]

api_urls = [
    re_path(
        route=r'^government/reference/$',
        name='government-reference-generate',
        view=APIGovernmentReferenceGenerateView.as_view()
    )
]
