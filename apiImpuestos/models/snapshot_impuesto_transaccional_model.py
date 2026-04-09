from django.db import models
from django.core.validators import MinValueValidator

from .impuesto_model import Impuesto


class SnapshotImpuestoTransaccional(models.Model):
    class Origen(models.TextChoices):
        PEDIDO_DETALLE = "PEDIDO_DETALLE", "Detalle de pedido"
        EMPLEADO_CONCEPTO = "EMPLEADO_CONCEPTO", "Concepto laboral empleado"

    impuesto = models.ForeignKey(
        Impuesto,
        on_delete=models.PROTECT,
        related_name="snapshots",
    )
    origen = models.CharField(max_length=40, choices=Origen.choices)
    origen_id = models.PositiveIntegerField()
    nombre_impuesto = models.CharField(max_length=100)
    codigo_impuesto = models.CharField(max_length=30)
    tipo_calculo = models.CharField(max_length=20, choices=Impuesto.TipoCalculo.choices)
    base_imponible = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    tasa_aplicada = models.DecimalField(max_digits=7, decimal_places=4, default=0, validators=[MinValueValidator(0)])
    monto_fijo_aplicado = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    monto_impuesto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    prioridad = models.PositiveIntegerField(default=100)
    acumulable = models.BooleanField(default=False)
    fecha_vigencia_inicio = models.DateField(null=True, blank=True)
    fecha_vigencia_fin = models.DateField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "tbl_snapshot_impuesto_transaccional"
        verbose_name = "Snapshot Impuesto Transaccional"
        verbose_name_plural = "Snapshots Impuesto Transaccional"
        ordering = ["-fecha_creacion", "id"]

    def __str__(self):
        return f"{self.origen}:{self.origen_id} {self.codigo_impuesto}={self.monto_impuesto}"

