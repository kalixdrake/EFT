from rest_framework import serializers

from apiAuditoria.models import EventoAuditoria


class EventoAuditoriaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = EventoAuditoria
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "endpoint",
            "metodo_http",
            "accion",
            "recurso",
            "resultado",
            "codigo_estado",
            "ip_origen",
            "user_agent",
            "metadata",
            "fecha_evento",
        ]
        read_only_fields = fields

