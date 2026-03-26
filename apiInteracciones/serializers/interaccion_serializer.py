from rest_framework import serializers
from apiInteracciones.models import InteraccionIA


class InteraccionIASerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = InteraccionIA
        fields = [
            'id',
            'fecha',
            'usuario_prompt',
            'contexto',
            'respuesta_ia',
            'acciones_ejecutadas',
            'exitosa',
            'archivo_adjunto',
            'archivo_url',
            'nombre_archivo_original'
        ]
        read_only_fields = ['id', 'fecha', 'contexto', 'respuesta_ia', 'acciones_ejecutadas']

    def get_archivo_url(self, obj):
        """Retorna la URL completa del archivo si existe"""
        if obj.archivo_adjunto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo_adjunto.url)
            return obj.archivo_adjunto.url
        return None


class InteraccionIAListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar interacciones"""
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = InteraccionIA
        fields = [
            'id',
            'fecha',
            'usuario_prompt',
            'respuesta_ia',
            'exitosa',
            'nombre_archivo_original',
            'archivo_url'
        ]

    def get_archivo_url(self, obj):
        if obj.archivo_adjunto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo_adjunto.url)
            return obj.archivo_adjunto.url
        return None
