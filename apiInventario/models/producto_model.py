from django.db import models
from django.core.validators import MinValueValidator
from apiUsuarios.models import Usuario


class Producto(models.Model):
    """
    Modelo para representar productos/items en el inventario.
    """
    
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del producto"
    )
    
    sku = models.CharField(
        max_length=100,
        unique=True,
        help_text="Código SKU único del producto"
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del producto"
    )
    
    precio_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Precio base del producto"
    )
    
    porcentaje_impuesto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Porcentaje de impuesto aplicable (ej: 16.00 para IVA 16%)"
    )
    
    stock_actual = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cantidad actual en inventario"
    )
    
    stock_minimo = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Stock mínimo antes de requerir reabastecimiento"
    )
    
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el producto está activo para la venta"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del producto"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización del producto"
    )
    
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        help_text="Imagen del producto"
    )
    
    class Meta:
        managed = True
        db_table = "tbl_productos"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} (SKU: {self.sku})"
    
    def precio_con_impuesto(self):
        """Calcula el precio incluyendo impuestos"""
        return self.precio_base * (1 + (self.porcentaje_impuesto / 100))
    
    def necesita_reabastecimiento(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo
    
    def valor_inventario(self):
        """Calcula el valor total del inventario actual"""
        return self.precio_base * self.stock_actual
