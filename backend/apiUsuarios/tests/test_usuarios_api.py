from django.test import TransactionTestCase
from django_bolt.testing import AsyncTestClient
from django_bolt.auth import create_jwt_for_user
from apiUsuarios.models.usuario_model import CustomUser
from EFT.api import api
from django.contrib.auth.hashers import make_password


SECURE_PASSWORD = "secure123"
SECURE_PASSWORD_HASH = make_password(SECURE_PASSWORD)

class UsuariosApiTests(TransactionTestCase):
    def setUp(self):
        # User with ADMIN business role.
        self.admin_user = CustomUser.objects.create(
            username="admin_user",
            email="admin@test.com",
            password=SECURE_PASSWORD_HASH,
            role=CustomUser.Roles.ADMIN,
            is_staff=True,
            is_active=True
        )

        # Internal non-admin staff user.
        self.empleado_user = CustomUser.objects.create(
            username="empleado_user",
            email="empleado@test.com",
            password=SECURE_PASSWORD_HASH,
            role=CustomUser.Roles.EMPLEADO,
            is_staff=True,
            is_active=True
        )

        # External user.
        self.cliente_user = CustomUser.objects.create(
            username="cliente",
            email="cliente@test.com",
            password=SECURE_PASSWORD_HASH,
            role=CustomUser.Roles.CLIENTE,
            is_staff=False,
            is_active=True
        )

    async def _get_auth_headers(self, username: str, password: str = SECURE_PASSWORD) -> dict:
        user = await CustomUser.objects.aget(username=username)
        token = create_jwt_for_user(user, expires_in=86400)
        return {"authorization": f"Bearer {token}"}

    async def test_login_success_returns_jwt(self):
        async with AsyncTestClient(api) as client:
            response = await client.post(
                "/api/auth/login",
                json={"username": "admin_user", "password": SECURE_PASSWORD}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("access_token", data)
            self.assertEqual(data["token_type"], "bearer")

    async def test_login_invalid_credentials(self):
        async with AsyncTestClient(api) as client:
            response = await client.post(
                "/api/auth/login",
                json={"username": "admin_user", "password": "wrong_password"}
            )
            self.assertEqual(response.status_code, 401)

    async def test_login_deactivated_user(self):
        await CustomUser.objects.filter(username="admin_user").aupdate(is_active=False)

        async with AsyncTestClient(api) as client:
            response = await client.post(
                "/api/auth/login",
                json={"username": "admin_user", "password": SECURE_PASSWORD}
            )
            self.assertEqual(response.status_code, 403)

    async def test_list_empleados_as_admin(self):
        headers = await self._get_auth_headers("admin_user", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.get(
                "/api/usuarios/empleados",
                headers=headers,
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()

            self.assertEqual(len(data), 2)
            usernames = [u["username"] for u in data]
            self.assertIn("admin_user", usernames)
            self.assertIn("empleado_user", usernames)
            self.assertNotIn("cliente", usernames)

    async def test_list_empleados_as_non_admin_is_forbidden(self):
        headers = await self._get_auth_headers("cliente", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.get(
                "/api/usuarios/empleados",
                headers=headers,
            )
            self.assertEqual(response.status_code, 403)

    async def test_create_empleado_as_admin(self):
        headers = await self._get_auth_headers("admin_user", "secure123")
        payload = {
            "username": "nuevo_empleado",
            "password": "strongpassword",
            "email": "nuevo@test.com",
            "first_name": "Nuevo",
            "last_name": "Empleado",
            "role": "Empleado",
            "phone": "1234567890"
        }
        async with AsyncTestClient(api) as client:
            response = await client.post(
                "/api/usuarios/empleados",
                json=payload,
                headers=headers,
            )
            self.assertEqual(response.status_code, 200)

            new_user = await CustomUser.objects.aget(username="nuevo_empleado")
            self.assertTrue(new_user.is_staff)
            self.assertEqual(new_user.role, "Empleado")

    async def test_usuario_puede_actualizar_su_perfil_sin_cambiar_rol(self):
        headers = await self._get_auth_headers("cliente", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.patch(
                f"/api/usuarios/{self.cliente_user.id}",
                json={"first_name": "Ana", "phone": "3001112233"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 200)
        await self.cliente_user.arefresh_from_db()
        self.assertEqual(self.cliente_user.first_name, "Ana")
        self.assertEqual(self.cliente_user.phone, "3001112233")

    async def test_usuario_no_puede_cambiar_su_propio_rol(self):
        headers = await self._get_auth_headers("cliente", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.patch(
                f"/api/usuarios/{self.cliente_user.id}",
                json={"role": "Administrador"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 403)
        await self.cliente_user.arefresh_from_db()
        self.assertEqual(self.cliente_user.role, CustomUser.Roles.CLIENTE)

    async def test_admin_puede_cambiar_rol_de_otro_usuario(self):
        headers = await self._get_auth_headers("admin_user", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.patch(
                f"/api/usuarios/{self.cliente_user.id}",
                json={"role": "Empleado"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 200)
        await self.cliente_user.arefresh_from_db()
        self.assertEqual(self.cliente_user.role, CustomUser.Roles.EMPLEADO)
        self.assertTrue(self.cliente_user.is_staff)

    async def test_desactivar_empleado_soft_delete(self):
        headers = await self._get_auth_headers("admin_user", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.delete(
                f"/api/usuarios/empleados/{self.empleado_user.id}/desactivar",
                headers=headers,
            )
            self.assertEqual(response.status_code, 200)

            await self.empleado_user.arefresh_from_db()
            self.assertFalse(self.empleado_user.is_active)

    async def test_no_admin_no_puede_desactivar_empleado(self):
        headers = await self._get_auth_headers("cliente", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.delete(
                f"/api/usuarios/empleados/{self.empleado_user.id}/desactivar",
                headers=headers,
            )

        self.assertEqual(response.status_code, 403)
        await self.empleado_user.arefresh_from_db()
        self.assertTrue(self.empleado_user.is_active)
