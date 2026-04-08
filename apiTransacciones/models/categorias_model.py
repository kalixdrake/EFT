from django.db import models

class Categoria(models.Model):
    """Categorías para clasificar transacciones"""
    
    class TipoCategoria(models.TextChoices):
        COSTO = 'COSTO', 'Costo Operativo'
        VENTA = 'VENTA', 'Venta/Ingreso'
        NOMINA = 'NOMINA', 'Nómina'
        IMPUESTOS = 'IMPUESTOS', 'Impuestos'
        GENERAL = 'GENERAL', 'General'
    
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)
    egreso = models.BooleanField()
    tipo = models.CharField(
        max_length=20,
        choices=TipoCategoria.choices,
        default=TipoCategoria.GENERAL,
        help_text="Tipo de categoría empresarial"
    )

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    class Meta:
        managed = True
        db_table = "tbl_categorias"
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
