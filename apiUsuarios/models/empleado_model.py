from django.db import models

from .usuario_model import Usuario


class Empleado(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        LICENCIA = "LICENCIA", "Licencia"
        INACTIVO = "INACTIVO", "Inactivo"

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="empleado",
        help_text="Usuario asociado a la entidad de negocio empleado",
    )
    numero_empleado = models.CharField(
        max_length=20,
        unique=True,
        help_text="Número único de empleado",
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
        help_text="Área o departamento del empleado",
    )
    fecha_contratacion = models.DateField(
        auto_now_add=True,
        help_text="Fecha de contratación",
    )
    salario_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Salario base del empleado",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        help_text="Estado laboral del empleado",
    )

    class Meta:
        managed = True
        db_table = "tbl_empleados"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["-fecha_contratacion"]

    def __str__(self):
        return f"{self.numero_empleado} - {self.usuario.get_full_name() or self.usuario.username}"
