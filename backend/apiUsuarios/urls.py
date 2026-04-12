from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet,
    ClienteViewSet,
    SocioViewSet,
    EmpleadoViewSet,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'socios', SocioViewSet, basename='socio')
router.register(r'empleados', EmpleadoViewSet, basename='empleado')

urlpatterns = [
    path('', include(router.urls)),
]
