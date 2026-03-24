from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de tus APIs (delegadas a cada app)
    path('api/', include('apiBancos.urls')),
    path('api/', include('apiCuentas.urls')),
    path('api/', include('apiTransacciones.urls')),
    path('api/', include('apiPresupuestos.urls')),

    path('chat/', include('apiInteracciones.urls')),

    # Endpoint para generar el esquema OpenAPI en crudo (JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Endpoint para acceder a la Interfaz Gráfica (Swagger)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

