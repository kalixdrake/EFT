from django.db import models

from apiUsuarios.models import Usuario

from .documento_model import Documento
from .version_documento_model import VersionDocumento


class AccesoDocumento(models.Model):
    class TipoEvento(models.TextChoices):
        VISUALIZACION = "VISUALIZACION", "Visualizacion"
        DESCARGA = "DESCARGA", "Descarga"

    documento = models.ForeignKey(
        Documento,
        on_delete=models.PROTECT,
        related_name="accesos",
    )
    version_documento = models.ForeignKey(
        VersionDocumento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accesos",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="accesos_documento",
    )
    tipo_evento = models.CharField(max_length=20, choices=TipoEvento.choices)
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "tbl_accesos_documento"
        ordering = ["-fecha_evento"]
        indexes = [
            models.Index(fields=["documento", "-fecha_evento"]),
            models.Index(fields=["usuario", "-fecha_evento"]),
        ]

    def __str__(self):
        return f"{self.tipo_evento} {self.documento.codigo} por {self.usuario.username}"

