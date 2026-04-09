from django.contrib import admin

from .models import (
    Ciudad,
    ClienteUbicacion,
    Departamento,
    EmpleadoUbicacion,
    Pais,
    SocioUbicacion,
    Ubicacion,
)

admin.site.register(Pais)
admin.site.register(Departamento)
admin.site.register(Ciudad)
admin.site.register(Ubicacion)
admin.site.register(ClienteUbicacion)
admin.site.register(SocioUbicacion)
admin.site.register(EmpleadoUbicacion)
