from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ImpuestoViewSet,
    ReglaImpuestoViewSet,
    AsignacionImpuestoViewSet,
    SnapshotImpuestoTransaccionalViewSet,
    ConceptoLaboralEmpleadoViewSet,
)

router = DefaultRouter()
router.register(r"impuestos", ImpuestoViewSet, basename="impuesto")
router.register(r"reglas-impuesto", ReglaImpuestoViewSet, basename="regla-impuesto")
router.register(r"asignaciones-impuesto", AsignacionImpuestoViewSet, basename="asignacion-impuesto")
router.register(r"snapshots-impuesto", SnapshotImpuestoTransaccionalViewSet, basename="snapshot-impuesto")
router.register(r"conceptos-laborales-empleado", ConceptoLaboralEmpleadoViewSet, basename="concepto-laboral-empleado")

urlpatterns = [
    path("", include(router.urls)),
]

