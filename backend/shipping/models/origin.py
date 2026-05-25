from django.db import models


class ShippingOrigin(models.Model):
    """
    Singleton — stores the dispatch origin address used for Skydropx quotes.
    Only one record is allowed. Edit it from the Django admin.
    """

    name = models.CharField('Nombre / Empresa', max_length=120)
    email = models.EmailField('Correo electrónico')
    phone = models.CharField('Teléfono', max_length=30)
    address = models.CharField('Dirección', max_length=255)
    city = models.CharField('Ciudad (area_level2/3)', max_length=120)
    state = models.CharField('Departamento (area_level1)', max_length=120)
    postal_code = models.CharField('Código postal', max_length=20)
    country_code = models.CharField('Código de país', max_length=5, default='CO')
    is_active = models.BooleanField('Activo', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Origen de envío'
        verbose_name_plural = 'Origen de envío'

    def __str__(self):
        return f'{self.name} — {self.city} ({self.postal_code})'

    def save(self, *args, **kwargs):
        # Enforce singleton: only one active origin at a time
        if self.is_active:
            ShippingOrigin.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()
