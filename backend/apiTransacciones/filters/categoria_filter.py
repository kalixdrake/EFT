import django_filters
from apiTransacciones.models.categorias_model import Categoria

class CategoriaFilter(django_filters.FilterSet):
    egreso = django_filters.BooleanFilter(field_name='egreso')

    class Meta:
        model = Categoria
        fields = ['egreso']
