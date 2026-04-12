from django.db import models
from django.core.validators import MinValueValidator

from apiUsuarios.models import Empleado


class ConceptoLaboralEmpleado(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="conceptos_laborales",
    )
    descripcion = models.CharField(max_length=200)
    monto_base = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    monto_impuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    fecha = models.DateField(auto_now_add=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_conceptos_laborales_empleado"
        verbose_name = "Concepto Laboral Empleado"
        verbose_name_plural = "Conceptos Laborales Empleado"
        ordering = ["-fecha_creacion", "id"]

    def __str__(self):
        return f"{self.empleado.numero_empleado} - {self.descripcion}"

