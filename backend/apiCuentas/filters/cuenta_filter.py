import django_filters
from apiCuentas.models.cuenta_model import Cuenta

class CuentaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    banco = django_filters.NumberFilter(field_name='banco__id')

    class Meta:
        model = Cuenta
        fields = ['nombre', 'banco']
