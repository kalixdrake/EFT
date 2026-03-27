from django.contrib import admin
from .models import Transaccion, Categoria, ProgramacionTransaccion

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'monto', 'categoria', 'cuenta', 'fecha_ejecucion')
    list_filter = ('categoria', 'cuenta', 'fecha_ejecucion')
    search_fields = ('descripcion',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'egreso')
    list_filter = ('egreso',)
    search_fields = ('nombre',)

@admin.register(ProgramacionTransaccion)
class ProgramacionTransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'monto', 'estado', 'frecuencia', 'fecha_programada', 'activa')
    list_filter = ('estado', 'frecuencia', 'activa', 'fecha_programada')
    search_fields = ('descripcion',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'fecha_ultima_ejecucion')
