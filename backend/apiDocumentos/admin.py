from django.contrib import admin

from .models import AccesoDocumento, Documento, TipoDocumento, VersionDocumento


admin.site.register(TipoDocumento)
admin.site.register(Documento)
admin.site.register(VersionDocumento)
admin.site.register(AccesoDocumento)

