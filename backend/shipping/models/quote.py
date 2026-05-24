import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class ShippingQuote(models.Model):
    quote_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='shipping_quotes', on_delete=models.CASCADE)
    carrier = models.CharField(max_length=120)
    service = models.CharField(max_length=120, blank=True)
    service_code = models.CharField(max_length=120, blank=True)
    estimated_days = models.PositiveIntegerField(default=0)
    cost_cop = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    skydropx_quote_id = models.CharField(max_length=120, blank=True)  # legacy
    skydropx_quotation_id = models.CharField(max_length=120, blank=True)  # UUID from POST /quotations
    skydropx_rate_id = models.CharField(max_length=120, blank=True)       # rate UUID for shipment creation
    destination_city = models.CharField(max_length=120)
    destination_postal_code = models.CharField(max_length=20, blank=True)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0.000'))
    dimensions = models.JSONField(default=dict, blank=True)
    shipping_credit_available = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.carrier} ({self.quote_id})'
