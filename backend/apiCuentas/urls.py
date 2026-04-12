from rest_framework import routers
from .views.CuentaViewset import CuentaViewSet

router = routers.DefaultRouter()
router.register(r'cuentas', CuentaViewSet, basename='cuenta')

urlpatterns = router.urls

