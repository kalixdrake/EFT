import django_filters
from apiPresupuestos.models.presupuesto_model import TransaccionProgramada

class PresupuestoFilter(django_filters.FilterSet):
    tipo = django_filters.NumberFilter(field_name='tipo_id')
    categoria = django_filters.NumberFilter(field_name='categoria_id')
    mes = django_filters.NumberFilter()
    estado = django_filters.CharFilter(lookup_expr='iexact')
    transaccion_aplicada_isnull = django_filters.BooleanFilter(field_name='transaccion_aplicada', lookup_expr='isnull')

    class Meta:
        model = TransaccionProgramada
        fields = ['tipo', 'categoria', 'mes', 'estado', 'transaccion_aplicada_isnull']
