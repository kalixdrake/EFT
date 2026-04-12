import django_filters
from apiTransacciones.models.programacion_model import ProgramacionTransaccion


class ProgramacionTransaccionFilter(django_filters.FilterSet):
    """Filter for programmed transactions"""
    
    fecha_min = django_filters.DateTimeFilter(field_name="fecha_programada", lookup_expr='gte')
    fecha_max = django_filters.DateTimeFilter(field_name="fecha_programada", lookup_expr='lte')
    monto_min = django_filters.NumberFilter(field_name="monto", lookup_expr='gte')
    monto_max = django_filters.NumberFilter(field_name="monto", lookup_expr='lte')
    descripcion = django_filters.CharFilter(field_name="descripcion", lookup_expr='icontains')
    categoria = django_filters.NumberFilter(field_name="categoria__id")
    cuenta = django_filters.NumberFilter(field_name="cuenta__id")
    estado = django_filters.ChoiceFilter(
        field_name="estado",
        choices=ProgramacionTransaccion.ESTADO_CHOICES
    )
    frecuencia = django_filters.ChoiceFilter(
        field_name="frecuencia",
        choices=ProgramacionTransaccion.FRECUENCIA_CHOICES
    )
    activa = django_filters.BooleanFilter(field_name="activa")
    fecha_creacion_min = django_filters.DateTimeFilter(field_name="fecha_creacion", lookup_expr='gte')
    fecha_creacion_max = django_filters.DateTimeFilter(field_name="fecha_creacion", lookup_expr='lte')

    class Meta:
        model = ProgramacionTransaccion
        fields = [
            'fecha_min', 'fecha_max', 'monto_min', 'monto_max', 
            'descripcion', 'categoria', 'cuenta', 'estado', 
            'frecuencia', 'activa', 'fecha_creacion_min', 'fecha_creacion_max'
        ]
