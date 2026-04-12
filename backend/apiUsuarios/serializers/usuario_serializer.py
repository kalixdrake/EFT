from rest_framework import serializers
from ..models import Usuario, Cliente, Socio, Empleado
from ..permissions import build_capabilities
from .cliente_serializer import ClienteSerializer
from .socio_serializer import SocioSerializer
from .empleado_serializer import EmpleadoSerializer


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer básico para el modelo Usuario"""
    
    cliente = ClienteSerializer(read_only=True, required=False)
    socio = SocioSerializer(read_only=True, required=False)
    empleado = EmpleadoSerializer(read_only=True, required=False)
    nombre_completo = serializers.SerializerMethodField()
    capabilities = serializers.SerializerMethodField()
    tipo_entidad = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'nombre_completo',
            'telefono', 'direccion', 'fecha_registro', 'activo_comercialmente',
            'cliente', 'socio', 'empleado', 'tipo_entidad',
            'is_active', 'capabilities'
        ]
        read_only_fields = ['id', 'fecha_registro']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username

    def get_capabilities(self, obj):
        return build_capabilities(obj)

    def get_tipo_entidad(self, obj):
        return obj.tipo_entidad_principal()


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos usuarios con contraseña"""
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    tipo_entidad = serializers.ChoiceField(
        choices=["CLIENTE", "SOCIO", "EMPLEADO"],
        required=True,
        write_only=True,
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'telefono', 'direccion',
            'activo_comercialmente', 'tipo_entidad'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        tipo_entidad = validated_data.pop('tipo_entidad')
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        if tipo_entidad == "CLIENTE":
            Cliente.objects.get_or_create(usuario=usuario)
        elif tipo_entidad == "SOCIO":
            Socio.objects.get_or_create(usuario=usuario)
        elif tipo_entidad == "EMPLEADO":
            Empleado.objects.get_or_create(
                usuario=usuario,
                defaults={"numero_empleado": f"EMP-{usuario.id}", "salario_base": 0},
            )
        return usuario


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar usuarios"""
    
    nombre_completo = serializers.SerializerMethodField()
    tipo_entidad = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre_completo', 'email', 'tipo_entidad', 'activo_comercialmente']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username

    def get_tipo_entidad(self, obj):
        return obj.tipo_entidad_principal()
