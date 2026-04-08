from django.db import models
from django.core.validators import MinValueValidator
from apiInventario.models import Producto
from .pedido_model import Pedido


class DetallePedido(models.Model):
    """
    Modelo para detalles de pedidos.
    Relaciona productos con pedidos y guarda el precio unitario del momento.
    """
    
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        help_text="Pedido al que pertenece este detalle"
    )
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
        help_text="Producto incluido en el pedido"
    )
    
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Cantidad de unidades del producto"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Precio unitario al momento del pedido (histórico)"
    )
    
    porcentaje_impuesto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Porcentaje de impuesto al momento del pedido"
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas específicas del producto en este pedido"
    )
    
    class Meta:
        managed = True
        db_table = "tbl_detalles_pedido"
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"
        unique_together = ['pedido', 'producto']
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - Pedido #{self.pedido.id}"
    
    def subtotal(self):
        """Calcula el subtotal sin impuestos"""
        return self.cantidad * self.precio_unitario
    
    def monto_impuesto(self):
        """Calcula el monto de impuestos"""
        return self.subtotal() * (self.porcentaje_impuesto / 100)
    
    def total(self):
        """Calcula el total incluyendo impuestos"""
        return self.subtotal() + self.monto_impuesto()
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe save para capturar el precio actual del producto
        si no se especifica uno.
        """
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_base
        
        if not self.porcentaje_impuesto:
            self.porcentaje_impuesto = self.producto.porcentaje_impuesto
        
        super().save(*args, **kwargs)
        
        # Recalcular el total del pedido
        self.pedido.calcular_total()
        self.pedido.save(update_fields=['total'])
