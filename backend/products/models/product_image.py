from django.db import models


class ProductImage(models.Model):
    product = models.ForeignKey('products.Product', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'Image {self.pk} for {self.product.name}'
