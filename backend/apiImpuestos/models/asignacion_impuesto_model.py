from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from apiInventario.models import Producto
from apiUsuarios.models import Empleado

from .impuesto_model import Impuesto
from .regla_impuesto_model import ReglaImpuesto


class AsignacionImpuesto(models.Model):
    class Ambito(models.TextChoices):
        PRODUCTO = "PRODUCTO", "Producto"
        EMPRESA = "EMPRESA", "Empresa"
        EMPLEADO = "EMPLEADO", "Empleado"

    regla = models.ForeignKey(
        ReglaImpuesto,
        on_delete=models.CASCADE,
        related_name="asignaciones",
    )
    ambito = models.CharField(max_length=20, choices=Ambito.choices)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="asignaciones_impuesto",
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="asignaciones_impuesto",
    )
    activo = models.BooleanField(default=True)
    prioridad_local = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)])
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_asignaciones_impuesto"
        verbose_name = "Asignacion de Impuesto"
        verbose_name_plural = "Asignaciones de Impuesto"
        ordering = ["prioridad_local", "id"]

    def __str__(self):
        return f"{self.ambito} -> {self.regla.impuesto.codigo}"

    def clean(self):
        if self.ambito == self.Ambito.PRODUCTO and not self.producto:
            raise ValidationError({"producto": "La asignacion de ambito PRODUCTO requiere producto."})
        if self.ambito == self.Ambito.EMPLEADO and not self.empleado:
            raise ValidationError({"empleado": "La asignacion de ambito EMPLEADO requiere empleado."})
        if self.ambito == self.Ambito.EMPRESA and (self.producto_id or self.empleado_id):
            raise ValidationError("La asignacion de ambito EMPRESA no debe tener producto ni empleado.")
        if self.regla.tipo_sujeto != self.ambito:
            raise ValidationError("El ambito debe coincidir con el tipo_sujeto de la regla.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

