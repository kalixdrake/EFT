from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccesoDocumentoViewSet, DocumentoViewSet, TipoDocumentoViewSet

router = DefaultRouter()
router.register(r"tipos-documento", TipoDocumentoViewSet, basename="tipo-documento")
router.register(r"documentos", DocumentoViewSet, basename="documento")
router.register(r"accesos-documento", AccesoDocumentoViewSet, basename="acceso-documento")

urlpatterns = [
    path("", include(router.urls)),
]

