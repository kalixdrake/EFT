from django.db import models

from .usuario_model import Usuario


class Cliente(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"
        SUSPENDIDO = "SUSPENDIDO", "Suspendido"

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cliente",
        help_text="Usuario asociado a la entidad de negocio cliente",
    )
    rif = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text="Identificador fiscal del cliente",
    )
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nombre comercial o razón social",
    )
    fecha_afiliacion = models.DateField(
        auto_now_add=True,
        help_text="Fecha de afiliación como cliente",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        help_text="Estado operativo del cliente",
    )

    class Meta:
        managed = True
        db_table = "tbl_clientes"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["-fecha_afiliacion"]

    def __str__(self):
        return self.nombre_comercial or self.usuario.get_full_name() or self.usuario.username
