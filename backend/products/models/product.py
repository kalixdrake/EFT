from decimal import Decimal

from django.db import models
from django.utils.text import slugify


class Product(models.Model):
    category = models.ForeignKey('products.Category', related_name='products', on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    box_length_cm = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    box_width_cm = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    box_height_cm = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0.000'))
    shipping_credit_cop = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sku = models.CharField(max_length=100, unique=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
