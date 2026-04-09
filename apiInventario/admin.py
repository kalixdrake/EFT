from django.contrib import admin

# Register your models here.
from .models import (
    Producto,
    MovimientoInventario,
    CategoriaActivo,
    ActivoFijo,
    DepreciacionActivo,
    MantenimientoActivo,
    MovimientoActivo,
)


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
            'fields': ('precio_base',)
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


@admin.register(CategoriaActivo)
class CategoriaActivoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "vida_util_meses", "tasa_depreciacion_anual", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre", "descripcion"]


@admin.register(ActivoFijo)
class ActivoFijoAdmin(admin.ModelAdmin):
    list_display = [
        "codigo_activo",
        "nombre",
        "tipo",
        "categoria",
        "estado",
        "asignado_a_empleado",
        "asignado_a_ubicacion",
        "valor_compra",
        "activo",
    ]
    list_filter = ["tipo", "estado", "categoria", "activo"]
    search_fields = ["codigo_activo", "nombre", "descripcion"]


@admin.register(DepreciacionActivo)
class DepreciacionActivoAdmin(admin.ModelAdmin):
    list_display = ["activo", "fecha", "metodo", "monto", "valor_en_libros"]
    list_filter = ["metodo", "fecha"]
    search_fields = ["activo__codigo_activo", "activo__nombre"]


@admin.register(MantenimientoActivo)
class MantenimientoActivoAdmin(admin.ModelAdmin):
    list_display = ["activo", "tipo", "estado", "fecha_programada", "fecha_ejecucion", "alerta_vencida", "costo"]
    list_filter = ["tipo", "estado", "alerta_vencida"]
    search_fields = ["activo__codigo_activo", "activo__nombre", "descripcion", "proveedor"]


@admin.register(MovimientoActivo)
class MovimientoActivoAdmin(admin.ModelAdmin):
    list_display = [
        "activo",
        "tipo",
        "responsable_anterior",
        "responsable_nuevo",
        "ubicacion_anterior",
        "ubicacion_nueva",
        "usuario",
        "fecha_movimiento",
    ]
    list_filter = ["tipo", "fecha_movimiento"]
    search_fields = ["activo__codigo_activo", "activo__nombre", "motivo"]

