from django.db import models
from django.core.validators import MinValueValidator
from apiUsuarios.models import Usuario
from .producto_model import Producto


class MovimientoInventario(models.Model):
    """
    Modelo para registrar movimientos de inventario (entradas y salidas).
    Proporciona trazabilidad completa de los cambios en stock.
    """
    
    class TipoMovimiento(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'
        AJUSTE = 'AJUSTE', 'Ajuste'
        DEVOLUCION = 'DEVOLUCION', 'Devolución'
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos',
        help_text="Producto afectado por el movimiento"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimiento.choices,
        help_text="Tipo de movimiento"
    )
    
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Cantidad de unidades movidas"
    )
    
    stock_anterior = models.IntegerField(
        help_text="Stock antes del movimiento"
    )
    
    stock_nuevo = models.IntegerField(
        help_text="Stock después del movimiento"
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='movimientos_inventario',
        help_text="Usuario interno/administrador que procesó el movimiento"
    )
    
    motivo = models.TextField(
        blank=True,
        null=True,
        help_text="Motivo o descripción del movimiento"
    )
    
    referencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Número de referencia (ej: número de pedido, factura)"
    )
    
    fecha_movimiento = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del movimiento"
    )
    
    class Meta:
        managed = True
        db_table = "tbl_movimientos_inventario"
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad} unidades) - {self.fecha_movimiento.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe save para actualizar automáticamente el stock del producto.
        """
        if not self.pk:  # Solo en creación
            # Guardar stock anterior
            self.stock_anterior = self.producto.stock_actual
            
            # Calcular nuevo stock según el tipo de movimiento
            if self.tipo in ['ENTRADA', 'DEVOLUCION']:
                self.stock_nuevo = self.stock_anterior + self.cantidad
            elif self.tipo == 'SALIDA':
                if self.stock_anterior < self.cantidad:
                    from django.core.exceptions import ValidationError
                    raise ValidationError(f"Stock insuficiente. Disponible: {self.stock_anterior}, Solicitado: {self.cantidad}")
                self.stock_nuevo = self.stock_anterior - self.cantidad
            elif self.tipo == 'AJUSTE':
                # Para ajustes, la cantidad representa el nuevo stock total
                self.stock_nuevo = self.cantidad
                self.cantidad = abs(self.stock_nuevo - self.stock_anterior)
            
            # Actualizar el stock del producto
            self.producto.stock_actual = self.stock_nuevo
            self.producto.save(update_fields=['stock_actual'])
        
        super().save(*args, **kwargs)
