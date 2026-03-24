from django.contrib import admin
from apiInteracciones.models import InteraccionIA

@admin.register(InteraccionIA)
class InteraccionIAAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'exitosa')

