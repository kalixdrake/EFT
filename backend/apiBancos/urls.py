from rest_framework import routers
from .views.BancoViewset import BancoViewSet

router = routers.DefaultRouter()
router.register(r'bancos', BancoViewSet, basename='banco')

urlpatterns = router.urls

