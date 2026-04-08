from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, PerfilSocio


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Administración personalizada para el modelo Usuario"""
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Empresarial', {
            'fields': ('rol', 'telefono', 'direccion', 'activo_comercialmente')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Empresarial', {
            'fields': ('rol', 'telefono', 'direccion', 'activo_comercialmente')
        }),
    )
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'activo_comercialmente', 'is_staff']
    list_filter = ['rol', 'activo_comercialmente', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telefono']


@admin.register(PerfilSocio)
class PerfilSocioAdmin(admin.ModelAdmin):
    """Administración para perfiles de socios"""
    
    list_display = ['usuario', 'porcentaje_anticipo', 'limite_credito', 'saldo_pendiente', 'activo', 'fecha_acuerdo']
    list_filter = ['activo', 'fecha_acuerdo']
    search_fields = ['usuario__username', 'usuario__email', 'usuario__first_name', 'usuario__last_name']
    readonly_fields = ['fecha_acuerdo', 'credito_disponible']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Acuerdos Comerciales', {
            'fields': ('porcentaje_anticipo', 'limite_credito', 'saldo_pendiente', 'descuento_especial')
        }),
        ('Información Adicional', {
            'fields': ('notas_internas', 'activo', 'fecha_acuerdo')
        }),
    )
    
    def credito_disponible(self, obj):
        return obj.credito_disponible()
    credito_disponible.short_description = 'Crédito Disponible'
