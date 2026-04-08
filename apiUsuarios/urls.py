from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, PerfilSocioViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'perfiles-socio', PerfilSocioViewSet, basename='perfil-socio')

urlpatterns = [
    path('', include(router.urls)),
]
