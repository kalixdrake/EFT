from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CiudadViewSet,
    ClienteUbicacionViewSet,
    DepartamentoViewSet,
    EmpleadoUbicacionViewSet,
    PaisViewSet,
    SocioUbicacionViewSet,
    UbicacionViewSet,
)

router = DefaultRouter()
router.register(r"paises", PaisViewSet, basename="pais")
router.register(r"departamentos", DepartamentoViewSet, basename="departamento")
router.register(r"ciudades", CiudadViewSet, basename="ciudad")
router.register(r"ubicaciones", UbicacionViewSet, basename="ubicacion")
router.register(r"clientes-ubicaciones", ClienteUbicacionViewSet, basename="cliente-ubicacion")
router.register(r"socios-ubicaciones", SocioUbicacionViewSet, basename="socio-ubicacion")
router.register(r"empleados-ubicaciones", EmpleadoUbicacionViewSet, basename="empleado-ubicacion")

urlpatterns = [
    path("", include(router.urls)),
]
