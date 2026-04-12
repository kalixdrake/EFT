from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from apiUsuarios.models import Usuario

class InteraccionIA(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="interacciones_ia",
        help_text="Usuario autenticado que realizó la interacción",
    )
    usuario_prompt = models.TextField(help_text="Petición del usuario")
    contexto = models.TextField(help_text="Contexto RAG enviado a la IA")
    respuesta_ia = models.TextField(help_text="Respuesta cruda de la IA")
    acciones_ejecutadas = models.TextField(blank=True, null=True, help_text="Acciones JSON o resumen de las operacines de backend")
    exitosa = models.BooleanField(default=True, help_text="Indica si la operación finalizó sin excepciones u errores de red")
    
    # Campos para adjuntos
    archivo_adjunto = models.FileField(
        upload_to='interacciones/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Archivo adjunto (recibos, comprobantes, excel, etc.)",
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'xlsx', 'xls', 'csv', 'jpg', 'jpeg', 'png', 'doc', 'docx']
        )]
    )
    nombre_archivo_original = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nombre original del archivo para referencia"
    )

    def __str__(self):
        return f"Interacción {self.id} - {self.usuario_id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-fecha']
