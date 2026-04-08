from django.db import models
from django.core.validators import MinValueValidator
from apiUsuarios.models import Usuario


class Nomina(models.Model):
    """
    Modelo para gestionar nóminas de empleados (usuarios internos y administradores).
    """
    
    class Periodicidad(models.TextChoices):
        SEMANAL = 'SEMANAL', 'Semanal'
        QUINCENAL = 'QUINCENAL', 'Quincenal'
        MENSUAL = 'MENSUAL', 'Mensual'
    
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PAGADO = 'PAGADO', 'Pagado'
        RETRASADO = 'RETRASADO', 'Retrasado'
    
    empleado = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        limit_choices_to={'rol__in': ['INTERNO', 'ADMINISTRADOR']},
        related_name='nominas',
        help_text="Empleado al que pertenece esta nómina"
    )
    
    salario_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Salario base del empleado"
    )
    
    periodicidad = models.CharField(
        max_length=20,
        choices=Periodicidad.choices,
        default=Periodicidad.QUINCENAL,
        help_text="Periodicidad de pago"
    )
    
    bonos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Bonos adicionales"
    )
    
    deducciones = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Deducciones (impuestos, préstamos, etc.)"
    )
    
    periodo_inicio = models.DateField(
        help_text="Fecha de inicio del periodo de pago"
    )
    
    periodo_fin = models.DateField(
        help_text="Fecha de fin del periodo de pago"
    )
    
    fecha_pago_programada = models.DateField(
        help_text="Fecha programada de pago"
    )
    
    fecha_pago_efectiva = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en que se realizó el pago efectivamente"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
        help_text="Estado del pago de nómina"
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas adicionales sobre esta nómina"
    )
    
    aprobado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'ADMINISTRADOR'},
        related_name='nominas_aprobadas',
        help_text="Administrador que aprobó el pago"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro"
    )
    
    class Meta:
        managed = True
        db_table = "tbl_nominas"
        verbose_name = "Nómina"
        verbose_name_plural = "Nóminas"
        ordering = ['-fecha_pago_programada']
        unique_together = ['empleado', 'periodo_inicio', 'periodo_fin']
    
    def __str__(self):
        return f"Nómina {self.empleado.get_full_name()} - {self.periodo_inicio} a {self.periodo_fin}"
    
    def salario_neto(self):
        """Calcula el salario neto (base + bonos - deducciones)"""
        return self.salario_base + self.bonos - self.deducciones
    
    def esta_vencido(self):
        """Verifica si el pago está retrasado"""
        from django.utils import timezone
        return self.estado == 'PENDIENTE' and self.fecha_pago_programada < timezone.now().date()
