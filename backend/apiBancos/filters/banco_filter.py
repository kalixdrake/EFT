import django_filters
from apiBancos.models.banco_model import Banco

class BancoFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Banco
        fields = ['nombre']
