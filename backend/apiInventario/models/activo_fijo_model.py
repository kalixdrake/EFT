from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apiUbicaciones.models import Ubicacion
from apiUsuarios.models import Empleado

from .categoria_activo_model import CategoriaActivo


class ActivoFijo(models.Model):
    class TipoActivo(models.TextChoices):
        VEHICULO = "VEHICULO", "Vehiculo"
        EQUIPO = "EQUIPO", "Equipo"
        COMPUTADOR = "COMPUTADOR", "Computador"
        OTRO = "OTRO", "Otro"

    class EstadoActivo(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        ASIGNADO = "ASIGNADO", "Asignado"
        EN_MANTENIMIENTO = "EN_MANTENIMIENTO", "En mantenimiento"
        INACTIVO = "INACTIVO", "Inactivo"
        BAJA = "BAJA", "Baja"

    codigo_activo = models.CharField(max_length=60, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TipoActivo.choices)
    categoria = models.ForeignKey(CategoriaActivo, on_delete=models.PROTECT, related_name="activos")
    estado = models.CharField(max_length=30, choices=EstadoActivo.choices, default=EstadoActivo.DISPONIBLE)

    valor_compra = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    valor_residual = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    fecha_adquisicion = models.DateField(default=timezone.now)

    asignado_a_empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activos_asignados",
    )
    asignado_a_ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activos_asignados",
    )

    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_activos_fijos"
        verbose_name = "Activo Fijo"
        verbose_name_plural = "Activos Fijos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo_activo} - {self.nombre}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.valor_residual > self.valor_compra:
            raise ValidationError("El valor residual no puede ser mayor al valor de compra.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def valor_depreciable(self):
        return self.valor_compra - self.valor_residual

    def depreciacion_mensual_estimado(self):
        vida = self.categoria.vida_util_meses or 1
        return self.valor_depreciable() / Decimal(vida)

