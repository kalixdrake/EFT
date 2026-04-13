from django_bolt import Router, Request
from django_bolt.auth import create_jwt_for_user
from django_bolt.serializers import Serializer
from django_bolt.exceptions import HTTPException
from django.contrib.auth import aauthenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

class LoginSerializer(Serializer):
    username: str
    password: str

class TokenResponseSerializer(Serializer):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

auth_router = Router(tags=["Autenticacion"])

@auth_router.post("/login", description="Login con usuario y contraseña y devolucion de token JWT")
async def login(request: Request, payload: LoginSerializer) -> TokenResponseSerializer:
    user = await aauthenticate(
        username=payload.username,
        password=payload.password
    )

    if not user:
        existing_user = await get_user_model().objects.filter(username=payload.username).afirst()
        if existing_user and not existing_user.is_active and check_password(payload.password, existing_user.password):
            raise HTTPException(
                status_code=403,
                detail="Cuenta desactivada."
            )

        raise HTTPException(
            status_code=401,
            detail="Credenciales invalidas."
        )

    if getattr(user, 'is_active', True) is False:
        raise HTTPException(
            status_code=403,
            detail="Cuenta desactivada."
        )

    # Usar el helper nativo de django_bolt
    token = create_jwt_for_user(user, expires_in=86400)

    return TokenResponseSerializer(
        access_token=token,
        expires_in=86400  # 1 dia
    )
