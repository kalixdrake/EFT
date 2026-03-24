from rest_framework import routers
from .views.presupuesto_viewset import PresupuestoViewSet

router = routers.DefaultRouter()
router.register(r'presupuestos', PresupuestoViewSet, basename='presupuestos')

urlpatterns = router.urls

