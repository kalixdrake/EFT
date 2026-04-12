from django.db import models

from apiUsuarios.models import Usuario

from .documento_model import Documento


class VersionDocumento(models.Model):
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name="versiones",
    )
    numero_version = models.PositiveIntegerField()
    archivo = models.FileField(upload_to="documentos/versiones/")
    hash_contenido = models.CharField(max_length=128, blank=True)
    observaciones = models.TextField(blank=True)
    usuario_editor = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="versiones_documento_editadas",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "tbl_versiones_documento"
        ordering = ["-numero_version", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["documento", "numero_version"],
                name="uniq_documento_numero_version",
            ),
        ]

    def __str__(self):
        return f"{self.documento.codigo} v{self.numero_version}"

