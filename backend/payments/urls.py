from django.urls import path

from payments.views import BoldWebhookAPIView


urlpatterns = [
    path('webhook/', BoldWebhookAPIView.as_view(), name='bold-webhook'),
]
