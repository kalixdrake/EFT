from django_bolt.serializers import Serializer

# Add absolute import since it is executed from the app models
from apiUsuarios.models.usuario_model import CustomUser

class UsuarioSerializer(Serializer):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    phone: str
    is_active: bool

class UsuarioCreateSerializer(Serializer):
    username: str
    password: str
    email: str
    first_name: str = ""
    last_name: str = ""
    role: str = CustomUser.Roles.CLIENTE
    phone: str = ""

class UsuarioUpdateSerializer(Serializer):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    phone: str | None = None
    is_active: bool | None = None
