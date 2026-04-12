from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apiUsuarios.models import Cliente, Empleado, Socio, Usuario

from .tipo_documento_model import TipoDocumento


class Documento(models.Model):
    class EstadoDocumento(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        PUBLICADO = "PUBLICADO", "Publicado"
        ARCHIVADO = "ARCHIVADO", "Archivado"

    codigo = models.CharField(max_length=60, unique=True)
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        related_name="documentos",
    )
    titulo = models.CharField(max_length=220)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoDocumento.choices,
        default=EstadoDocumento.BORRADOR,
    )
    fecha_vencimiento = models.DateField(null=True, blank=True)
    ultima_version = models.PositiveIntegerField(default=1)
    archivo_actual = models.FileField(upload_to="documentos/actual/")
    hash_contenido = models.CharField(max_length=128, blank=True)

    propietario_empresa = models.BooleanField(default=False)
    propietario_empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos",
    )
    propietario_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos",
    )
    propietario_socio = models.ForeignKey(
        Socio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos",
    )

    usuario_creador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="documentos_creados",
    )
    usuario_actualizador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="documentos_actualizados",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_documentos"
        ordering = ["-fecha_actualizacion"]

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"

    @property
    def usuario_propietario(self):
        if self.propietario_empleado_id:
            return self.propietario_empleado.usuario
        if self.propietario_cliente_id:
            return self.propietario_cliente.usuario
        if self.propietario_socio_id:
            return self.propietario_socio.usuario
        return self.usuario_creador

    @property
    def requiere_alerta_vencimiento(self):
        if not self.fecha_vencimiento:
            return False
        dias_alerta = self.tipo_documento.dias_alerta_vencimiento
        return self.fecha_vencimiento <= timezone.now().date() + timedelta(days=dias_alerta)

    def clean(self):
        propietarios = [
            bool(self.propietario_empresa),
            bool(self.propietario_empleado_id),
            bool(self.propietario_cliente_id),
            bool(self.propietario_socio_id),
        ]
        total = sum(1 for p in propietarios if p)
        if total != 1:
            raise ValidationError("Debe existir exactamente un propietario para el documento.")

        permitido = self.tipo_documento.propietario_permitido
        if permitido == TipoDocumento.TipoPropietario.UNIVERSAL:
            pass
        elif permitido == TipoDocumento.TipoPropietario.EMPRESA and not self.propietario_empresa:
            raise ValidationError("El tipo de documento requiere propietario EMPRESA.")
        elif permitido == TipoDocumento.TipoPropietario.EMPLEADO and not self.propietario_empleado_id:
            raise ValidationError("El tipo de documento requiere propietario EMPLEADO.")
        elif permitido == TipoDocumento.TipoPropietario.CLIENTE and not self.propietario_cliente_id:
            raise ValidationError("El tipo de documento requiere propietario CLIENTE.")
        elif permitido == TipoDocumento.TipoPropietario.SOCIO and not self.propietario_socio_id:
            raise ValidationError("El tipo de documento requiere propietario SOCIO.")

        if self.tipo_documento.requiere_vencimiento and not self.fecha_vencimiento:
            raise ValidationError("Este tipo de documento requiere fecha de vencimiento.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
