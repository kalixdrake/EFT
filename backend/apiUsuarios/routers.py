from django_bolt import Router, Request
from django_bolt.auth import IsAuthenticated
from django_bolt.exceptions import HTTPException
from django.contrib.auth.hashers import make_password
from apiUsuarios.models.usuario_model import CustomUser
from apiUsuarios.serializers.usuario_serializer import UsuarioSerializer, UsuarioCreateSerializer, UsuarioUpdateSerializer
from asgiref.sync import sync_to_async

usuarios_router = Router(tags=["Usuarios"])


def _es_admin(usuario: CustomUser) -> bool:
    return bool(usuario.is_superuser or usuario.role == CustomUser.Roles.ADMIN)


def _es_rol_interno(role: str) -> bool:
    return role in {
        CustomUser.Roles.ADMIN,
        CustomUser.Roles.CONTADOR,
        CustomUser.Roles.ABOGADO,
        CustomUser.Roles.EMPLEADO,
    }

@usuarios_router.get("/empleados", guards=[IsAuthenticated()])
async def listar_empleados(request: Request) -> list[UsuarioSerializer]:
    if not _es_admin(request.user):
        raise HTTPException(status_code=403, detail="Solo administradores pueden listar empleados")

    # Use asgiref to handle synchronous ORM query or use async Django ORM
    empleados = await sync_to_async(list)(
        CustomUser.objects.filter(is_staff=True).only(
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_active'
        )
    )
    return empleados

@usuarios_router.get("/{user_id}", guards=[IsAuthenticated()])
async def detalle_usuario(request: Request, user_id: int) -> UsuarioSerializer:
    actor = request.user
    if actor.id != user_id and not _es_admin(actor):
        raise HTTPException(status_code=403, detail="No tienes permisos para consultar este usuario")

    try:
        usuario = await CustomUser.objects.aget(id=user_id)
    except CustomUser.DoesNotExist:
        raise HTTPException(status_code=404, detail="Usuario not found")

    return usuario

@usuarios_router.post("/empleados", guards=[IsAuthenticated()])
async def crear_empleado(request: Request, payload: UsuarioCreateSerializer) -> UsuarioSerializer:
    if not _es_admin(request.user):
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear empleados")

    if not _es_rol_interno(payload.role):
        raise HTTPException(status_code=400, detail="El rol del empleado debe ser interno")

    usuario = CustomUser(
        username=payload.username,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role,
        phone=payload.phone,
        is_staff=True,
    )
    usuario.password = make_password(payload.password)
    await usuario.asave()
    return usuario

@usuarios_router.patch("/{user_id}", guards=[IsAuthenticated()])
async def editar_perfil(request: Request, user_id: int, payload: UsuarioUpdateSerializer) -> UsuarioSerializer:
    try:
        usuario = await CustomUser.objects.aget(id=user_id)
    except CustomUser.DoesNotExist:
        raise HTTPException(status_code=404, detail="Usuario not found")

    actor = request.user
    actor_is_admin = _es_admin(actor)

    if actor.id != usuario.id and not actor_is_admin:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar este perfil")

    if payload.email is not None:
        usuario.email = payload.email
    if payload.first_name is not None:
        usuario.first_name = payload.first_name
    if payload.last_name is not None:
        usuario.last_name = payload.last_name
    if payload.phone is not None:
        usuario.phone = payload.phone

    if payload.role is not None:
        if actor.id == usuario.id:
            raise HTTPException(status_code=403, detail="No puedes cambiar tu propio rol")
        if not actor_is_admin:
            raise HTTPException(status_code=403, detail="Solo administradores pueden cambiar roles")

        usuario.role = payload.role
        usuario.is_staff = _es_rol_interno(payload.role)

    if payload.is_active is not None:
        if not actor_is_admin:
            raise HTTPException(status_code=403, detail="Solo administradores pueden cambiar el estado")
        usuario.is_active = payload.is_active

    await usuario.asave()
    return usuario

@usuarios_router.delete("/empleados/{user_id}/desactivar", guards=[IsAuthenticated()])
async def desactivar_empleado(request: Request, user_id: int) -> dict:
    if not _es_admin(request.user):
        raise HTTPException(status_code=403, detail="Solo administradores pueden desactivar empleados")

    try:
        usuario = await CustomUser.objects.aget(id=user_id)
    except CustomUser.DoesNotExist:
        raise HTTPException(status_code=404, detail="Usuario not found")

    usuario.is_active = False
    await usuario.asave()
    return {"status": "desactivado", "id": usuario.id}
