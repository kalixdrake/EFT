from django.conf import settings
from django.db import models

from .municipality import Municipality


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='addresses', on_delete=models.CASCADE)
    municipality = models.ForeignKey(Municipality, related_name='addresses', on_delete=models.PROTECT)
    line = models.CharField(max_length=255)
    label = models.CharField(max_length=50, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-updated_at']
        verbose_name_plural = 'addresses'

    def __str__(self):
        label = f' ({self.label})' if self.label else ''
        return f'{self.line}{label} — {self.user}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(user_id=self.user_id).exclude(pk=self.pk).update(is_default=False)
