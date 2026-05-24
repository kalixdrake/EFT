from decimal import Decimal

from django.db import models


class Shipment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PICKED_UP = 'picked_up', 'Picked up'
        IN_TRANSIT = 'in_transit', 'In transit'
        DELIVERED = 'delivered', 'Delivered'

    class PackageType(models.TextChoices):
        BOX = 'box', 'Box'
        MERCHANDISE = 'merchandise', 'Merchandise'

    order = models.OneToOneField('orders.Order', related_name='shipment', on_delete=models.CASCADE)
    carrier = models.CharField(max_length=120, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True, null=True, unique=True)
    label_url = models.URLField(blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    estimated_days = models.PositiveIntegerField(default=0)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0.000'))
    package_type = models.CharField(max_length=30, choices=PackageType.choices, default=PackageType.BOX)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    skydropx_shipment_id = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f'Shipment #{self.pk}'
