from rest_framework import routers
from .views.transaccion_viewset import TransaccionViewSet
from .views.categoria_viewset import CategoriaViewSet

router = routers.DefaultRouter()
router.register(r'transacciones', TransaccionViewSet, basename='transaccion')
router.register(r'categorias', CategoriaViewSet, basename='categoria')

urlpatterns = router.urls

