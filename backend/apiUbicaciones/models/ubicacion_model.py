from apiUbicaciones.models.municipio_model import Municipio
from apiUsuarios.models.usuario_model import CustomUser
from django.db import models


class Ubicacion(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ubicaciones")
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    street = models.TextField()
    country = models.CharField(max_length=2, default="CO")
    postalCode = models.CharField(max_length=20, help_text="Postal code", null=True, blank=True)

    # Optional fields mapping from Geocodes API
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    @property
    def city(self):
        return self.municipio.nombre

    @property
    def state(self):
        return self.municipio.departamento.nombre