from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoViewSet,
    MovimientoInventarioViewSet,
    CategoriaActivoViewSet,
    ActivoFijoViewSet,
    DepreciacionActivoViewSet,
    MantenimientoActivoViewSet,
    MovimientoActivoViewSet,
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'movimientos-inventario', MovimientoInventarioViewSet, basename='movimiento-inventario')
router.register(r'categorias-activo', CategoriaActivoViewSet, basename='categoria-activo')
router.register(r'activos-fijos', ActivoFijoViewSet, basename='activo-fijo')
router.register(r'depreciaciones-activo', DepreciacionActivoViewSet, basename='depreciacion-activo')
router.register(r'mantenimientos-activo', MantenimientoActivoViewSet, basename='mantenimiento-activo')
router.register(r'movimientos-activo', MovimientoActivoViewSet, basename='movimiento-activo')

urlpatterns = [
    path('', include(router.urls)),
]
