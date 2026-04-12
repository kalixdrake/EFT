from django.core.exceptions import ValidationError
from django.db import models

from apiUsuarios.models import Cliente, Empleado, Socio


class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_iso = models.CharField(max_length=3, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = "tbl_paises"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="departamentos")
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = "tbl_departamentos"
        ordering = ["nombre"]
        unique_together = [("pais", "nombre")]

    def __str__(self):
        return f"{self.nombre}, {self.pais.nombre}"


class Ciudad(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, related_name="ciudades")
    nombre = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=12, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = "tbl_ciudades"
        ordering = ["nombre"]
        unique_together = [("departamento", "nombre")]

    def __str__(self):
        return f"{self.nombre}, {self.departamento.nombre}"


class Ubicacion(models.Model):
    class Tipo(models.TextChoices):
        ENTREGA = "ENTREGA", "Entrega"
        FACTURACION = "FACTURACION", "Facturacion"
        OPERATIVA = "OPERATIVA", "Operativa"

    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, related_name="ubicaciones")
    nombre = models.CharField(max_length=150)
    direccion = models.TextField()
    referencia = models.CharField(max_length=255, blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.ENTREGA)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = "tbl_ubicaciones"
        ordering = ["nombre"]
        unique_together = [("ciudad", "nombre", "direccion")]

    def __str__(self):
        return f"{self.nombre} - {self.ciudad.nombre}"


class _EntidadUbicacionBase(models.Model):
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name="+")
    es_principal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def _validate_single_principal(self, model_cls, entidad_field):
        if not self.es_principal:
            return
        filters = {entidad_field: getattr(self, entidad_field), "es_principal": True}
        qs = model_cls.objects.filter(**filters)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError("Solo se permite una ubicación principal por entidad.")


class ClienteUbicacion(_EntidadUbicacionBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="ubicaciones")

    class Meta:
        managed = True
        db_table = "tbl_cliente_ubicaciones"
        unique_together = [("cliente", "ubicacion")]

    def clean(self):
        self._validate_single_principal(ClienteUbicacion, "cliente")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class SocioUbicacion(_EntidadUbicacionBase):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name="ubicaciones")

    class Meta:
        managed = True
        db_table = "tbl_socio_ubicaciones"
        unique_together = [("socio", "ubicacion")]

    def clean(self):
        self._validate_single_principal(SocioUbicacion, "socio")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class EmpleadoUbicacion(_EntidadUbicacionBase):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="ubicaciones")

    class Meta:
        managed = True
        db_table = "tbl_empleado_ubicaciones"
        unique_together = [("empleado", "ubicacion")]

    def clean(self):
        self._validate_single_principal(EmpleadoUbicacion, "empleado")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
