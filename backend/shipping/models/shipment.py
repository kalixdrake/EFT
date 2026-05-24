from decimal import Decimal

from django.db import models


class Shipment(models.Model):
    order = models.OneToOneField('orders.Order', related_name='shipment', on_delete=models.CASCADE)
    carrier = models.CharField(max_length=120, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True)
    label_url = models.URLField(blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    estimated_days = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=30, default='pending')

    def __str__(self):
        return f'Shipment #{self.pk}'