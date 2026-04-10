from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventoAuditoriaViewSet

router = DefaultRouter()
router.register(r"auditoria-eventos", EventoAuditoriaViewSet, basename="auditoria-evento")

urlpatterns = [
    path("", include(router.urls)),
]

