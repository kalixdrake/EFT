from rest_framework import routers
from .views.transaccion_viewset import TransaccionViewSet, TipoTransaccionViewSet, CategoriaTransaccionViewSet

router = routers.DefaultRouter()
router.register(r'transacciones', TransaccionViewSet, basename='transaccion')
router.register(r'tipos-transaccion', TipoTransaccionViewSet, basename='tipo_transaccion')
router.register(r'categorias-transaccion', CategoriaTransaccionViewSet, basename='categoria_transaccion')

urlpatterns = router.urls

