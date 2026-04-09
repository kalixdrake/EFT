from django.db import models
from django.core.validators import MinValueValidator

from .impuesto_model import Impuesto


class ReglaImpuesto(models.Model):
    class BaseImponible(models.TextChoices):
        SUBTOTAL = "SUBTOTAL", "Subtotal"
        SUBTOTAL_MENOS_DESCUENTO = "SUBTOTAL_MENOS_DESCUENTO", "Subtotal menos descuento"
        TOTAL_ACTUAL = "TOTAL_ACTUAL", "Total actual acumulado"
        SALARIO_BASE = "SALARIO_BASE", "Salario base"
        MONTO_EXPLICITO = "MONTO_EXPLICITO", "Monto explicito"

    impuesto = models.ForeignKey(
        Impuesto,
        on_delete=models.CASCADE,
        related_name="reglas",
    )
    tipo_sujeto = models.CharField(max_length=20, choices=Impuesto.TipoSujeto.choices)
    base_imponible = models.CharField(max_length=40, choices=BaseImponible.choices, default=BaseImponible.SUBTOTAL)
    prioridad = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)])
    acumulable = models.BooleanField(default=False)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_reglas_impuesto"
        verbose_name = "Regla de Impuesto"
        verbose_name_plural = "Reglas de Impuesto"
        ordering = ["prioridad", "id"]

    def __str__(self):
        return f"{self.impuesto.codigo} [{self.tipo_sujeto}] p{self.prioridad}"

