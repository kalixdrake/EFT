import django_filters
from apiTransacciones.models.transaccion_model import Transaccion

class TransaccionFilter(django_filters.FilterSet):
    fecha_min = django_filters.DateTimeFilter(field_name="fecha_ejecucion", lookup_expr='gte')
    fecha_max = django_filters.DateTimeFilter(field_name="fecha_ejecucion", lookup_expr='lte')
    monto_min = django_filters.NumberFilter(field_name="monto", lookup_expr='gte')
    monto_max = django_filters.NumberFilter(field_name="monto", lookup_expr='lte')
    descripcion = django_filters.CharFilter(field_name="descripcion", lookup_expr='icontains')
    categoria = django_filters.NumberFilter(field_name="categoria__id")
    cuenta = django_filters.NumberFilter(field_name="cuenta__id")

    class Meta:
        model = Transaccion
        fields = ['fecha_min', 'fecha_max', 'monto_min', 'monto_max', 'descripcion', 'categoria', 'cuenta']
