from rest_framework import routers
from .views.transaccion_viewset import TransaccionViewSet
from .views.categoria_viewset import CategoriaViewSet
from .views.programacion_viewset import ProgramacionTransaccionViewSet
from .views.nomina_viewset import NominaViewSet

router = routers.DefaultRouter()
router.register(r'transacciones', TransaccionViewSet, basename='transaccion')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'programaciones', ProgramacionTransaccionViewSet, basename='programacion')
router.register(r'nominas', NominaViewSet, basename='nomina')

urlpatterns = router.urls

