from django.contrib import admin

# Register your models here.
from .models import Producto, MovimientoInventario


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Administración para Productos"""
    
    list_display = ['nombre', 'sku', 'precio_base', 'stock_actual', 'stock_minimo', 'activo']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'sku', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'sku', 'descripcion', 'imagen')
        }),
        ('Precios', {
            'fields': ('precio_base', 'porcentaje_impuesto')
        }),
        ('Inventario', {
            'fields': ('stock_actual', 'stock_minimo', 'activo')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    """Administración para Movimientos de Inventario"""
    
    list_display = ['producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha_movimiento']
    list_filter = ['tipo', 'fecha_movimiento']
    search_fields = ['producto__nombre', 'producto__sku', 'motivo', 'referencia']
    readonly_fields = ['stock_anterior', 'stock_nuevo', 'fecha_movimiento']
    
    # No permitir edición ni eliminación para mantener trazabilidad
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

