from django.contrib import admin
from .models import Pedido, DetallePedido


class DetallePedidoInline(admin.TabularInline):
    """Inline para detalles de pedido"""
    model = DetallePedido
    extra = 1
    readonly_fields = ['subtotal', 'monto_impuesto', 'total']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Administración para Pedidos"""
    
    list_display = ['id', 'tipo', 'estado', 'cliente', 'total', 'monto_pagado', 'fecha_creacion']
    list_filter = ['tipo', 'estado', 'fecha_creacion']
    search_fields = ['cliente__username', 'cliente__email', 'notas']
    readonly_fields = ['total', 'fecha_creacion', 'fecha_actualizacion', 'fecha_completado']
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('tipo', 'estado', 'cliente', 'interno_asignado')
        }),
        ('Montos', {
            'fields': ('total', 'monto_pagado', 'porcentaje_descuento')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion', 'fecha_completado'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    """Administración para Detalles de Pedido"""
    
    list_display = ['pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['pedido__tipo', 'pedido__estado']
    search_fields = ['pedido__id', 'producto__nombre', 'producto__sku']

