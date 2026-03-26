from apiTransacciones.models.categorias_model import Categoria
from apiTransacciones.serializers.categoria_serializer import CategoriaSerializer
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apiTransacciones.filters.categoria_filter import CategoriaFilter

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoriaFilter
    serializer_class = CategoriaSerializer