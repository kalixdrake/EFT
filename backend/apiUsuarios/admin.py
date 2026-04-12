from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Cliente, Socio, Empleado


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Administración personalizada para el modelo Usuario"""
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Empresarial', {
            'fields': ('telefono', 'direccion', 'activo_comercialmente')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Empresarial', {
            'fields': ('telefono', 'direccion', 'activo_comercialmente')
        }),
    )
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'activo_comercialmente', 'is_staff']
    list_filter = ['activo_comercialmente', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telefono']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'nombre_comercial', 'rif', 'estado', 'fecha_afiliacion']
    list_filter = ['estado', 'fecha_afiliacion']
    search_fields = ['usuario__username', 'usuario__email', 'nombre_comercial', 'rif']


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'limite_credito', 'saldo_pendiente', 'activo', 'fecha_acuerdo']
    list_filter = ['activo', 'fecha_acuerdo']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['fecha_acuerdo']


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'numero_empleado', 'departamento', 'estado', 'fecha_contratacion']
    list_filter = ['estado', 'departamento', 'fecha_contratacion']
    search_fields = ['usuario__username', 'usuario__email', 'numero_empleado']
