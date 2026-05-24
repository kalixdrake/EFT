from decimal import Decimal

from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        PENDING_DELIVERY = 'pending_delivery', 'Pending delivery'

    order = models.OneToOneField('orders.Order', related_name='payment', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=120, blank=True, null=True, unique=True)
    bold_reference = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='COP')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment #{self.pk}'


class PaymentLog(models.Model):
    payment = models.ForeignKey(Payment, related_name='logs', on_delete=models.CASCADE)
    event = models.CharField(max_length=120)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'PaymentLog #{self.pk} ({self.event})'
