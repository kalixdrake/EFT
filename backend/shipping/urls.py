from django.urls import path

from shipping.views import ShippingQuoteAPIView


urlpatterns = [
    path('quote/', ShippingQuoteAPIView.as_view(), name='shipping-quote'),
]
