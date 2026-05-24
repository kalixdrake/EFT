from decimal import Decimal

from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    order = models.OneToOneField('orders.Order', related_name='payment', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=120, blank=True)
    bold_reference = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f'Payment #{self.pk}'