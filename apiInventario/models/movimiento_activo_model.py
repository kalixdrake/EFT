from django.db import models
from django.utils import timezone

from apiUbicaciones.models import Ubicacion
from apiUsuarios.models import Empleado, Usuario

from .activo_fijo_model import ActivoFijo


class MovimientoActivo(models.Model):
    class TipoMovimiento(models.TextChoices):
        ASIGNACION = "ASIGNACION", "Asignacion"
        REASIGNACION = "REASIGNACION", "Reasignacion"
        TRASLADO = "TRASLADO", "Traslado"
        MANTENIMIENTO = "MANTENIMIENTO", "Mantenimiento"
        BAJA = "BAJA", "Baja"

    activo = models.ForeignKey(ActivoFijo, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=20, choices=TipoMovimiento.choices)
    responsable_anterior = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_activo_como_anterior",
    )
    responsable_nuevo = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_activo_como_nuevo",
    )
    ubicacion_anterior = models.ForeignKey(
        Ubicacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_activo_como_ubicacion_anterior",
    )
    ubicacion_nueva = models.ForeignKey(
        Ubicacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_activo_como_ubicacion_nueva",
    )
    motivo = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="movimientos_activo")
    fecha_movimiento = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = "tbl_movimientos_activo"
        verbose_name = "Movimiento de Activo"
        verbose_name_plural = "Movimientos de Activo"
        ordering = ["-fecha_movimiento", "-id"]

    def __str__(self):
        return f"{self.activo.codigo_activo} - {self.tipo}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.responsable_anterior = self.activo.asignado_a_empleado
            self.ubicacion_anterior = self.activo.asignado_a_ubicacion

            if self.tipo in [self.TipoMovimiento.ASIGNACION, self.TipoMovimiento.REASIGNACION]:
                self.activo.asignado_a_empleado = self.responsable_nuevo
                if self.responsable_nuevo:
                    self.activo.estado = ActivoFijo.EstadoActivo.ASIGNADO
            if self.tipo == self.TipoMovimiento.TRASLADO:
                self.activo.asignado_a_ubicacion = self.ubicacion_nueva
            if self.tipo == self.TipoMovimiento.MANTENIMIENTO:
                self.activo.estado = ActivoFijo.EstadoActivo.EN_MANTENIMIENTO
            if self.tipo == self.TipoMovimiento.BAJA:
                self.activo.estado = ActivoFijo.EstadoActivo.BAJA
                self.activo.activo = False

            self.activo.save()
        super().save(*args, **kwargs)

