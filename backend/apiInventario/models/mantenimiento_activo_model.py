from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .activo_fijo_model import ActivoFijo


class MantenimientoActivo(models.Model):
    class Tipo(models.TextChoices):
        PREVENTIVO = "PREVENTIVO", "Preventivo"
        CORRECTIVO = "CORRECTIVO", "Correctivo"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_PROCESO = "EN_PROCESO", "En proceso"
        COMPLETADO = "COMPLETADO", "Completado"
        CANCELADO = "CANCELADO", "Cancelado"

    activo = models.ForeignKey(ActivoFijo, on_delete=models.CASCADE, related_name="mantenimientos")
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    descripcion = models.TextField()
    proveedor = models.CharField(max_length=150, blank=True, null=True)
    costo = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    fecha_programada = models.DateField()
    fecha_ejecucion = models.DateField(null=True, blank=True)
    proximo_mantenimiento = models.DateField(null=True, blank=True)
    alerta_vencida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_mantenimientos_activo"
        verbose_name = "Mantenimiento de Activo"
        verbose_name_plural = "Mantenimientos de Activo"
        ordering = ["fecha_programada", "id"]

    def __str__(self):
        return f"{self.activo.codigo_activo} - {self.tipo} ({self.estado})"

    def actualizar_alerta(self):
        hoy = timezone.now().date()
        self.alerta_vencida = self.estado in [self.Estado.PENDIENTE, self.Estado.EN_PROCESO] and self.fecha_programada < hoy
        return self.alerta_vencida

    def save(self, *args, **kwargs):
        self.actualizar_alerta()
        super().save(*args, **kwargs)

