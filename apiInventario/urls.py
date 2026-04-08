from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, MovimientoInventarioViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'movimientos-inventario', MovimientoInventarioViewSet, basename='movimiento-inventario')

urlpatterns = [
    path('', include(router.urls)),
]
