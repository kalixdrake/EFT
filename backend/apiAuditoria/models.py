from django.db import models

from apiUsuarios.models import Usuario


class EventoAuditoria(models.Model):
    class ResultadoEvento(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FORBIDDEN = "FORBIDDEN", "Forbidden"
        ERROR = "ERROR", "Error"

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_auditoria",
    )
    endpoint = models.CharField(max_length=255)
    metodo_http = models.CharField(max_length=10)
    accion = models.CharField(max_length=80)
    recurso = models.CharField(max_length=80)
    resultado = models.CharField(max_length=20, choices=ResultadoEvento.choices)
    codigo_estado = models.PositiveSmallIntegerField()
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "tbl_eventos_auditoria"
        ordering = ["-fecha_evento"]
        indexes = [
            models.Index(fields=["-fecha_evento"]),
            models.Index(fields=["recurso", "accion", "-fecha_evento"]),
            models.Index(fields=["usuario", "-fecha_evento"]),
            models.Index(fields=["resultado", "-fecha_evento"]),
        ]

    def __str__(self):
        user = self.usuario.username if self.usuario else "anon"
        return f"{self.recurso}:{self.accion}:{self.resultado} by {user}"

