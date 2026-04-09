from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Impuesto(models.Model):
    class TipoImpuesto(models.TextChoices):
        IVA = "IVA", "IVA"
        RETENCION = "RETENCION", "Retencion"
        ARANCEL = "ARANCEL", "Arancel"
        CONTRIBUCION = "CONTRIBUCION", "Contribucion"
        OTRO = "OTRO", "Otro"

    class TipoCalculo(models.TextChoices):
        PERCENTAGE = "PERCENTAGE", "Porcentaje"
        FIXED = "FIXED", "Fijo"

    class TipoSujeto(models.TextChoices):
        PRODUCTO = "PRODUCTO", "Producto"
        EMPRESA = "EMPRESA", "Empresa"
        EMPLEADO = "EMPLEADO", "Empleado"

    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=30, unique=True)
    tipo_impuesto = models.CharField(max_length=20, choices=TipoImpuesto.choices)
    tipo_calculo = models.CharField(max_length=20, choices=TipoCalculo.choices, default=TipoCalculo.PERCENTAGE)
    tasa = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Tasa porcentual cuando tipo_calculo=PERCENTAGE.",
    )
    monto_fijo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Monto fijo cuando tipo_calculo=FIXED.",
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_impuestos"
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

