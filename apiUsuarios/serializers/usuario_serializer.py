from rest_framework import serializers
from ..models import Usuario, PerfilSocio


class PerfilSocioSerializer(serializers.ModelSerializer):
    """Serializer para el perfil de socio"""
    
    credito_disponible = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        source='credito_disponible'
    )
    
    class Meta:
        model = PerfilSocio
        fields = [
            'id', 'porcentaje_anticipo', 'limite_credito', 'saldo_pendiente',
            'credito_disponible', 'descuento_especial', 'fecha_acuerdo', 'activo'
        ]
        read_only_fields = ['id', 'fecha_acuerdo', 'credito_disponible']


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer básico para el modelo Usuario"""
    
    perfil_socio = PerfilSocioSerializer(read_only=True, required=False)
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'nombre_completo',
            'rol', 'telefono', 'direccion', 'fecha_registro', 'activo_comercialmente',
            'perfil_socio', 'is_active'
        ]
        read_only_fields = ['id', 'fecha_registro']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos usuarios con contraseña"""
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'rol', 'telefono', 'direccion',
            'activo_comercialmente'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar usuarios"""
    
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre_completo', 'email', 'rol', 'activo_comercialmente']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username
