from django.db import models
from apiCuentas.models.cuenta_model import Cuenta
from apiTransacciones.models.transaccion_model import Transaccion, TipoTransaccion, CategoriaTransaccion

class TransaccionProgramada(models.Model):
    ESTADO_CHOICES = [
        ('PROGRAMADA', 'Programada'),
        ('EJECUTADA', 'Ejecutada'),
        ('CANCELADA', 'Cancelada'),
    ]

    TIPO_PERIODO_CHOICES = [
        ('DIA', 'Día Exacto'),
        ('SEMANA', 'Semana del Mes'),
        ('MES', 'Mes Completo'),
    ]

    # Datos base de la transacción
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    tipo = models.ForeignKey(TipoTransaccion, on_delete=models.PROTECT, related_name='programadas')
    categoria = models.ForeignKey(CategoriaTransaccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='programadas')
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='programadas')

    # Datos de programación
    tipo_periodo = models.CharField(max_length=15, choices=TIPO_PERIODO_CHOICES, default='MES')
    anio = models.IntegerField()
    mes = models.IntegerField()
    semana = models.IntegerField(null=True, blank=True, help_text='1 al 5 dependiendo de la semana del mes')
    fecha_exacta = models.DateField(null=True, blank=True, help_text='Usar cuando tipo_periodo es DIA')

    # Estado y relación al ejecutarse
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PROGRAMADA')
    transaccion_aplicada = models.OneToOneField(
        Transaccion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='programada_origen',
        help_text='Transacción real generada al ejecutarse'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.estado}] {self.descripcion} - {self.monto}"

    class Meta:
        managed = True
        db_table = 'tbl_transacciones_programadas'

