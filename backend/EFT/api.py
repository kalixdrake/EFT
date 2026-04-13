from django_bolt import BoltAPI
from apiUsuarios.routers import usuarios_router
from apiUsuarios.auth_router import auth_router
from apiUbicaciones.routers import ubicaciones_router
from django.core.asgi import get_asgi_application

api = BoltAPI()

# Register auth backend for JWT
api._register_auth_backends()

# Register routers
api.include_router(auth_router, prefix="/api/auth")
api.include_router(usuarios_router, prefix="/api/usuarios")
api.include_router(ubicaciones_router, prefix="/api/ubicaciones")

# Mount classic Django apps (Admin panel, standard views) onto Bolt ASGI
api.mount_django("/django", get_asgi_application())
