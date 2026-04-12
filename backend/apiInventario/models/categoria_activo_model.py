from django.core.validators import MinValueValidator
from django.db import models


class CategoriaActivo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    vida_util_meses = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        help_text="Vida útil estimada en meses para depreciación lineal.",
    )
    tasa_depreciacion_anual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Porcentaje anual referencial.",
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_categorias_activo"
        verbose_name = "Categoria de Activo"
        verbose_name_plural = "Categorias de Activo"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

