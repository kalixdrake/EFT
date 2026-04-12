from django.contrib import admin

from .models import (
    Impuesto,
    ReglaImpuesto,
    AsignacionImpuesto,
    SnapshotImpuestoTransaccional,
    ConceptoLaboralEmpleado,
)


@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "tipo_impuesto", "tipo_calculo", "tasa", "monto_fijo", "activo"]
    list_filter = ["tipo_impuesto", "tipo_calculo", "activo"]
    search_fields = ["codigo", "nombre"]


@admin.register(ReglaImpuesto)
class ReglaImpuestoAdmin(admin.ModelAdmin):
    list_display = ["impuesto", "tipo_sujeto", "base_imponible", "prioridad", "acumulable", "fecha_inicio", "fecha_fin", "activo"]
    list_filter = ["tipo_sujeto", "base_imponible", "acumulable", "activo"]
    search_fields = ["impuesto__codigo", "impuesto__nombre"]


@admin.register(AsignacionImpuesto)
class AsignacionImpuestoAdmin(admin.ModelAdmin):
    list_display = ["regla", "ambito", "producto", "empleado", "prioridad_local", "activo"]
    list_filter = ["ambito", "activo"]
    search_fields = ["regla__impuesto__codigo", "regla__impuesto__nombre", "producto__sku", "empleado__numero_empleado"]


@admin.register(SnapshotImpuestoTransaccional)
class SnapshotImpuestoTransaccionalAdmin(admin.ModelAdmin):
    list_display = ["origen", "origen_id", "codigo_impuesto", "base_imponible", "monto_impuesto", "fecha_creacion"]
    list_filter = ["origen", "codigo_impuesto"]
    search_fields = ["codigo_impuesto", "nombre_impuesto"]
    readonly_fields = [
        "impuesto",
        "origen",
        "origen_id",
        "nombre_impuesto",
        "codigo_impuesto",
        "tipo_calculo",
        "base_imponible",
        "tasa_aplicada",
        "monto_fijo_aplicado",
        "monto_impuesto",
        "prioridad",
        "acumulable",
        "fecha_vigencia_inicio",
        "fecha_vigencia_fin",
        "metadata",
        "fecha_creacion",
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConceptoLaboralEmpleado)
class ConceptoLaboralEmpleadoAdmin(admin.ModelAdmin):
    list_display = ["empleado", "descripcion", "monto_base", "monto_impuesto", "monto_total", "fecha"]
    list_filter = ["fecha"]
    search_fields = ["empleado__numero_empleado", "descripcion"]

