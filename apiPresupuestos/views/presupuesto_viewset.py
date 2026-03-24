from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from apiPresupuestos.models.presupuesto_model import TransaccionProgramada
from apiPresupuestos.serializers.presupuesto_serializer import TransaccionProgramadaSerializer
from apiTransacciones.models.transaccion_model import Transaccion
from apiPresupuestos.filters.presupuesto_filter import PresupuestoFilter

class PresupuestoViewSet(viewsets.ModelViewSet):
    queryset = TransaccionProgramada.objects.all()
    serializer_class = TransaccionProgramadaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PresupuestoFilter

    @action(detail=True, methods=['patch'], url_path='ejecutar')
    def ejecutar(self, request, pk=None):
        programada = self.get_object()

        if programada.estado != 'PROGRAMADA':
            return Response(
                {'error': f'La transacción ya está {programada.estado.lower()}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear la transacción real
        transaccion = Transaccion.objects.create(
            monto=programada.monto,
            descripcion=programada.descripcion,
            tipo=programada.tipo,
            categoria=programada.categoria,
            cuenta=programada.cuenta
        )

        # Actualizar estado
        programada.estado = 'EJECUTADA'
        programada.transaccion_aplicada = transaccion
        programada.save()

        return Response(
            {'status': 'Transacción ejecutada con éxito', 'transaccion_id': transaccion.id}, 
            status=status.HTTP_200_OK
        )


    @action(detail=False, methods=['post'], url_path='crear-repetitivas')
    def crear_repetitivas(self, request):
        data = request.data
        
        required_fields = ['monto', 'descripcion', 'tipo', 'cuenta', 'tipo_periodo', 'anio', 'mes_inicio', 'mes_fin']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return Response(
                {"error": f"Faltan campos requeridos: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            monto_base = float(data['monto'])
            anio = int(data['anio'])
            mes_inicio = int(data['mes_inicio'])
            mes_fin = int(data['mes_fin'])
            porcentaje = float(data.get('porcentaje')) if data.get('porcentaje') else None
            transaccion_base_desc = data.get('transaccion_base_descripcion', '')
        except ValueError as e:
            return Response({"error": f"Error de formato en los datos: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        instancias = []
        for mes in range(mes_inicio, mes_fin + 1):
            monto_calcular = monto_base

            if porcentaje is not None and transaccion_base_desc:
                qs = TransaccionProgramada.objects.filter(
                    anio=anio,
                    mes=mes,
                    descripcion__icontains=transaccion_base_desc
                )
                suma = qs.aggregate(total=Sum('monto'))['total']
                if suma and suma > 0:
                    monto_calcular = float(suma) * (porcentaje / 100.0)

            nueva_prog = TransaccionProgramada(
                monto=monto_calcular,
                descripcion=data['descripcion'],
                tipo_id=data['tipo'],
                categoria_id=data.get('categoria'),
                cuenta_id=data['cuenta'],
                tipo_periodo=data['tipo_periodo'],
                anio=anio,
                mes=mes,
                estado='PROGRAMADA'
            )
            instancias.append(nueva_prog)

        try:
            creadas = TransaccionProgramada.objects.bulk_create(instancias)
            return Response(
                {"status": "success", "mensaje": f"Se crearon {len(creadas)} transacciones programadas exitosamente."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Error al guardar: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

