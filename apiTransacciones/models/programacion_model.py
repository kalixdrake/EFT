from django.db import models
from django.utils.timezone import now
from apiCuentas.models.cuenta_model import Cuenta
from .categorias_model import Categoria


class ProgramacionTransaccion(models.Model):
    """Modelo para transacciones programadas/futuras"""
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EJECUTADA', 'Ejecutada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    FRECUENCIA_CHOICES = [
        ('UNICA', 'Única'),
        ('DIARIA', 'Diaria'),
        ('SEMANAL', 'Semanal'),
        ('QUINCENAL', 'Quincenal'),
        ('MENSUAL', 'Mensual'),
        ('TRIMESTRAL', 'Trimestral'),
        ('ANUAL', 'Anual'),
    ]
    
    monto = models.DecimalField(max_digits=32, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_programada = models.DateTimeField()
    fecha_proximo_intento = models.DateTimeField(null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='programaciones')
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='programaciones')
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    
    frecuencia = models.CharField(
        max_length=20,
        choices=FRECUENCIA_CHOICES,
        default='UNICA'
    )
    
    fecha_ultima_ejecucion = models.DateTimeField(null=True, blank=True)
    fecha_fin_repeticion = models.DateTimeField(null=True, blank=True)
    
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Programación - {self.descripcion} - {self.monto} - {self.estado}"
    
    class Meta:
        managed = True
        db_table = "tbl_programaciones_transacciones"
        ordering = ['-fecha_programada']
