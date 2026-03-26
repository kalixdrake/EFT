from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apiTransacciones.models.transaccion_model import Transaccion
from apiTransacciones.serializers.transaccion_serializer import TransaccionSerializer
from apiTransacciones.serializers.transferencia_serializer import TransferenciaSerializer
from apiTransacciones.filters.transaccion_filter import TransaccionFilter

class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = TransaccionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransaccionFilter

    @action(detail=False, methods=['post'], url_path='transferir')
    def transferir(self, request):
        serializer = TransferenciaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Transferencia creada exitosamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='ejecutar')
    def ejecutar(self, request, pk=None):
        transaccion = self.get_object()
        serializer = EjecutarTransaccionSerializer(transaccion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Transacción ejecutada exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)