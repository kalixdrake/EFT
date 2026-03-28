
from apiTransacciones.models.programacion_model import ProgramacionTransaccion
from apiTransacciones.helpers.next_date import _calculate_next_date
from apiTransacciones.serializers.transaccion_serializer import TransaccionSerializer
import calendar
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from apiTransacciones.helpers.recurring_ocurrences import get_recurring_occurrences

class ProgramacionTransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacionTransaccion
        fields = '__all__'
    
    def validate(self, data):
        """
        Validate programmed transaction data
        """
        fecha_programada = data.get('fecha_programada')
        categoria = data.get('categoria')
        cuenta = data.get('cuenta')
        monto = data.get('monto')
        frecuencia = data.get('frecuencia', 'UNICA')
        fecha_fin_repeticion = data.get('fecha_fin_repeticion')
        
        # Convert string dates if necessary
        if isinstance(fecha_programada, str):
            try:
                fecha_programada = datetime.fromisoformat(fecha_programada.replace('Z', '+00:00'))
                data['fecha_programada'] = fecha_programada
            except ValueError:
                raise serializers.ValidationError({'fecha_programada': 'Formato de fecha inválido'})
        
        # Validate that fecha_programada is in the future
        if fecha_programada and fecha_programada <= timezone.now():
            raise serializers.ValidationError({'fecha_programada': 'La fecha programada debe ser en el futuro'})
        
        # Validate monto
        if monto and monto <= 0:
            raise serializers.ValidationError({'monto': 'El monto debe ser mayor a cero'})
        
        # Validate that categoria and cuenta exist
        if not categoria:
            raise serializers.ValidationError({'categoria': 'La categoría es requerida'})
        if not cuenta:
            raise serializers.ValidationError({'cuenta': 'La cuenta es requerida'})
        
        # Validate for recurrent transactions
        if frecuencia != 'UNICA':
            if not fecha_fin_repeticion:
                raise serializers.ValidationError({'fecha_fin_repeticion': 'La fecha de fin de repetición es requerida para transacciones recurrentes'})
            
            if isinstance(fecha_fin_repeticion, str):
                try:
                    fecha_fin_repeticion = datetime.fromisoformat(fecha_fin_repeticion.replace('Z', '+00:00'))
                    data['fecha_fin_repeticion'] = fecha_fin_repeticion
                except ValueError:
                    raise serializers.ValidationError({'fecha_fin_repeticion': 'Formato de fecha inválido'})
            
            if fecha_fin_repeticion <= fecha_programada:
                raise serializers.ValidationError({'fecha_fin_repeticion': 'La fecha de fin debe ser posterior a la fecha programada'})
        
        return data


class ProgramacionTransaccionListSerializer(serializers.ModelSerializer):
    """Serializer for list view with minimal fields"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre', read_only=True)
    
    class Meta:
        model = ProgramacionTransaccion
        fields = [
            'id', 'monto', 'descripcion', 'fecha_programada', 
            'estado', 'frecuencia', 'categoria_nombre', 'cuenta_nombre',
            'activa'
        ]


class ProgramacionTransaccionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view with all fields"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre', read_only=True)
    
    class Meta:
        model = ProgramacionTransaccion
        fields = '__all__'

class PresupuestoConsolidadoPorCuentaSerializer(serializers.Serializer):
    cuenta = serializers.SerializerMethodField()
    total_gastos_mes_actual = serializers.DecimalField(max_digits=32, decimal_places=2)
    total_gastos_siguiente_mes = serializers.DecimalField(max_digits=32, decimal_places=2)
    excedente_presupuestal_mes_actual = serializers.DecimalField(max_digits=32, decimal_places=2)
    excedente_presupuestal_siguiente_mes = serializers.DecimalField(max_digits=32, decimal_places=2)
    excedente_general = serializers.DecimalField(max_digits=32, decimal_places=2)
    transacciones_programadas_mes_actual = serializers.ListField(child=serializers.DictField())
    transacciones_programadas_mes_siguiente = serializers.ListField(child=serializers.DictField())

    def get_cuenta(self, obj):
        return {
            'id': obj.id,
            'nombre': obj.nombre,
            'saldo': obj.saldo
        }

    def to_representation(self, instance):
        """
        instance is a Cuenta object.
        We compute the metrics using the programaciones passed via context.
        """
        programaciones = self.context.get('programaciones', [])
        today = timezone.now().date()

        # --- Rango del mes actual (desde hoy hasta fin de mes) ---
        current_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        if today.month == 12:
            current_end_date = datetime(today.year, 12, 31).date()
        else:
            current_end_date = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
        current_end = timezone.make_aware(datetime.combine(current_end_date, datetime.max.time()))

        # --- Rango del mes siguiente ---
        if today.month == 12:
            next_month_start = datetime(today.year + 1, 1, 1).date()
        else:
            next_month_start = datetime(today.year, today.month + 1, 1).date()
        _, last_day = calendar.monthrange(next_month_start.year, next_month_start.month)
        next_month_end = datetime(next_month_start.year, next_month_start.month, last_day).date()
        next_start = timezone.make_aware(datetime.combine(next_month_start, datetime.min.time()))
        next_end = timezone.make_aware(datetime.combine(next_month_end, datetime.max.time()))

        gastos_actual = Decimal('0.00')
        gastos_siguiente = Decimal('0.00')
        ingresos_actual = Decimal('0.00')
        ingresos_siguiente = Decimal('0.00')
        transacciones_actual = []
        transacciones_siguiente = []

        # Filtrar programaciones de esta cuenta
        for prog in programaciones:
            if prog.cuenta.id != instance.id:
                continue

            es_egreso = prog.categoria.egreso
            monto = prog.monto

            if prog.frecuencia == 'UNICA':
                fecha = prog.fecha_programada
                if current_start <= fecha <= current_end:
                    if es_egreso:
                        gastos_actual += monto
                    else:
                        ingresos_actual += monto
                    transacciones_actual.append(self._build_transaction_dict(prog, fecha))
                elif next_start <= fecha <= next_end:
                    if es_egreso:
                        gastos_siguiente += monto
                    else:
                        ingresos_siguiente += monto
                    transacciones_siguiente.append(self._build_transaction_dict(prog, fecha))
            else:
                # Recurrente
                for fecha in get_recurring_occurrences(prog, current_start, current_end):
                    if es_egreso:
                        gastos_actual += monto
                    else:
                        ingresos_actual += monto
                    transacciones_actual.append(self._build_transaction_dict(prog, fecha))

                for fecha in get_recurring_occurrences(prog, next_start, next_end):
                    if es_egreso:
                        gastos_siguiente += monto
                    else:
                        ingresos_siguiente += monto
                    transacciones_siguiente.append(self._build_transaction_dict(prog, fecha))

        saldo = instance.saldo
        excedente_actual = saldo - gastos_actual
        excedente_siguiente = ingresos_siguiente - gastos_siguiente
        excedente_general = excedente_actual + excedente_siguiente

        data = {
            'cuenta': self.get_cuenta(instance),
            'total_gastos_mes_actual': gastos_actual,
            'total_gastos_siguiente_mes': gastos_siguiente,
            'excedente_presupuestal_mes_actual': excedente_actual,
            'excedente_presupuestal_siguiente_mes': excedente_siguiente,
            'excedente_general': excedente_general,
            'transacciones_programadas_mes_actual': transacciones_actual,
            'transacciones_programadas_mes_siguiente': transacciones_siguiente,
        }
        return data

    def _build_transaction_dict(self, programacion, fecha):
        return {
            'id': programacion.id,
            'fecha': fecha.isoformat(),
            'monto': programacion.monto,
            'descripcion': programacion.descripcion,
            'categoria': programacion.categoria.nombre,
            'tipo': 'gasto' if programacion.categoria.egreso else 'ingreso',
        }


class EjecutarProgramacionSerializer(serializers.Serializer):
    """
    Serializer para ejecutar una transacción programada.
    Realiza todas las validaciones y la creación de la transacción.
    """
    fecha_ejecucion = serializers.DateTimeField(required=False, input_formats=['iso-8601'])

    def validate(self, attrs):
        # Obtener la programación desde el contexto
        programacion = self.context.get('programacion')
        if not programacion:
            raise serializers.ValidationError('No se proporcionó la programación.')

        # Validar estado y activación
        if programacion.estado != 'PENDIENTE':
            raise serializers.ValidationError(
                f'No se puede ejecutar una transacción en estado {programacion.estado}.'
            )
        if not programacion.activa:
            raise serializers.ValidationError(
                'La transacción programada está desactivada.'
            )

        # Fecha de ejecución: si no se envía, usar ahora
        fecha = attrs.get('fecha_ejecucion')
        if fecha is None:
            fecha = timezone.now()
        attrs['fecha_ejecucion'] = fecha

        return attrs

    def create(self, validated_data):
        programacion = self.context.get('programacion')
        fecha_ejecucion = validated_data['fecha_ejecucion']

        # Crear la transacción real
        try:
            transaccion_data = {
                'monto': programacion.monto,
                'descripcion': programacion.descripcion,
                'fecha_ejecucion': fecha_ejecucion,
                'categoria': programacion.categoria.id,
                'cuenta': programacion.cuenta.id,
                'programacion': programacion.id,
            }
            trans_serializer = TransaccionSerializer(data=transaccion_data)
            trans_serializer.is_valid(raise_exception=True)
            transaccion = trans_serializer.save()
        except Exception as e:
            raise serializers.ValidationError(f'Error al crear la transacción: {str(e)}')

        # Manejar recurrencia
        if programacion.frecuencia == 'UNICA':
            programacion.estado = 'EJECUTADA'
            programacion.activa = False
            programacion.fecha_ultima_ejecucion = fecha_ejecucion
            message = 'Transacción ejecutada y programación finalizada.'
        else:
            # Calcular próxima fecha
            next_date = _calculate_next_date(programacion.fecha_programada, programacion.frecuencia)
            if programacion.fecha_fin_repeticion and next_date > programacion.fecha_fin_repeticion:
                programacion.estado = 'EJECUTADA'
                programacion.activa = False
                message = 'Transacción ejecutada. La recurrencia ha finalizado.'
            else:
                programacion.fecha_programada = next_date
                programacion.fecha_ultima_ejecucion = fecha_ejecucion
                message = f'Transacción ejecutada. Próxima ejecución programada para {next_date}'

        programacion.save()

        return {
            'transaccion': transaccion,
            'programacion': programacion,
            'message': message,
        }