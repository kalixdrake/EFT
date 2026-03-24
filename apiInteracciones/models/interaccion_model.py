from django.db import models
from django.utils import timezone

class InteraccionIA(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    usuario_prompt = models.TextField(help_text="Petición del usuario")
    contexto = models.TextField(help_text="Contexto RAG enviado a la IA")
    respuesta_ia = models.TextField(help_text="Respuesta cruda de la IA")
    acciones_ejecutadas = models.TextField(blank=True, null=True, help_text="Acciones JSON o resumen de las operacines de backend")
    exitosa = models.BooleanField(default=True, help_text="Indica si la operación finalizó sin excepciones u errores de red")

    def __str__(self):
        return f"Interacción {self.id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

