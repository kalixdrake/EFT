from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apiUsuarios.models import Usuario
from apiUbicaciones.models import Ubicacion


class Pedido(models.Model):
    """
    Modelo para representar pedidos/órdenes en el sistema.
    Soporta diferentes tipos según entidad/permiso del usuario.
    """
    
    class TipoPedido(models.TextChoices):
        VENTA_CLIENTE = 'VENTA_CLIENTE', 'Venta a Cliente'
        RE_STOCK = 'RE_STOCK', 'Reabastecimiento'
        APARTADO_SOCIO = 'APARTADO_SOCIO', 'Apartado de Socio'
    
    class EstadoPedido(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PENDIENTE_APROBACION = 'PENDIENTE_APROBACION', 'Pendiente de Aprobación'
        APROBADO = 'APROBADO', 'Aprobado'
        PAGADO_PARCIAL = 'PAGADO_PARCIAL', 'Pago Parcial'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoPedido.choices,
        help_text="Tipo de pedido"
    )
    
    estado = models.CharField(
        max_length=30,
        choices=EstadoPedido.choices,
        default=EstadoPedido.PENDIENTE,
        help_text="Estado actual del pedido"
    )
    
    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='pedidos_como_cliente',
        help_text="Cliente o proveedor asociado al pedido"
    )

    ubicacion_entrega = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="pedidos_entrega",
        help_text="Ubicación de entrega del pedido",
    )
    
    interno_asignado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to=models.Q(empleado__isnull=False),
        related_name='pedidos_asignados',
        help_text="Usuario interno/admin asignado al pedido"
    )
    
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Total del pedido (calculado automáticamente)"
    )
    
    monto_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Monto ya pagado del pedido"
    )
    
    porcentaje_descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Porcentaje de descuento aplicado"
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas adicionales sobre el pedido"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del pedido"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización del pedido"
    )
    
    fecha_completado = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se completó el pedido"
    )
    
    class Meta:
        managed = True
        db_table = "tbl_pedidos"
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.get_tipo_display()} - {self.cliente.username}"
    
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de pago"""
        return self.total - self.monto_pagado
    
    def esta_pagado(self):
        """Verifica si el pedido está completamente pagado"""
        return self.monto_pagado >= self.total
    
    def calcular_total(self):
        """Calcula el total basado en los detalles del pedido"""
        from django.db.models import Sum, F
        
        subtotal = self.detalles.aggregate(
            total=Sum(F('cantidad') * F('precio_unitario'))
        )['total'] or 0
        impuestos = self.detalles.aggregate(
            total=Sum('monto_impuesto')
        )['total'] or 0
        
        # Aplicar descuento
        descuento_pct = Decimal(str(self.porcentaje_descuento or 0))
        descuento = subtotal * (descuento_pct / Decimal("100"))
        self.total = (subtotal - descuento) + impuestos
        return self.total
