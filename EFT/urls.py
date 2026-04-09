from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de tus APIs (delegadas a cada app)
    path('api/', include('apiUsuarios.urls')),
    path('api/', include('apiInventario.urls')),
    path('api/', include('apiPedidos.urls')),
    path('api/', include('apiImpuestos.urls')),
    path('api/', include('apiUbicaciones.urls')),
    path('api/', include('apiBancos.urls')),
    path('api/', include('apiCuentas.urls')),
    path('api/', include('apiTransacciones.urls')),

    path('chat/', include('apiInteracciones.urls')),

    # Endpoint para generar el esquema OpenAPI en crudo (JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Endpoint para acceder a la Interfaz Gráfica (Swagger)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

