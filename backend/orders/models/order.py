from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PENDING_COD = 'pending_cod', 'Pending COD'
        CONFIRMED = 'confirmed', 'Confirmed'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    class PaymentMethod(models.TextChoices):
        BOLD = 'bold', 'Bold'
        COD = 'cod', 'COD'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    address = models.ForeignKey('locations.Address', related_name='orders', on_delete=models.PROTECT)
    shipping_quote = models.ForeignKey(
        'shipping.ShippingQuote',
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    order_number = models.CharField(max_length=32, unique=True, editable=False, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_cost_before_credit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_credit_applied = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_free_shipping = models.BooleanField(default=False)
    shipping_method = models.CharField(max_length=120, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BOLD)
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def item_count(self):
        cached_count = self.__dict__.get('item_count')
        if cached_count is not None:
            return cached_count
        return self.items.count()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and not self.order_number:
            created = self.created_at or timezone.now()
            if timezone.is_aware(created):
                created = timezone.localtime(created)
            self.order_number = f'{created.strftime("%d%m%Y")}-{self.pk}'
            super().save(update_fields=['order_number'])

    def __str__(self):
        return self.order_number or f'Order #{self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='order_items', on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
