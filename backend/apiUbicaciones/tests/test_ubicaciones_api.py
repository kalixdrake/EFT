from django.test import TransactionTestCase
from django_bolt.testing import AsyncTestClient
from django_bolt.auth import create_jwt_for_user
from apiUsuarios.models.usuario_model import CustomUser
from apiUbicaciones.models.departamento_model import Departamento
from apiUbicaciones.models.municipio_model import Municipio
from apiUbicaciones.models.ubicacion_model import Ubicacion
from EFT.api import api
from django.contrib.auth.hashers import make_password


SECURE_PASSWORD = "secure123"
SECURE_PASSWORD_HASH = make_password(SECURE_PASSWORD)

class UbicacionesApiTests(TransactionTestCase):
    def setUp(self):
        self.departamento = Departamento.objects.create(codigo_dane="05", nombre="Antioquia")
        self.municipio_medellin = Municipio.objects.create(
            codigo_dane="05001",
            departamento=self.departamento,
            nombre="MEDELLIN",
        )
        self.municipio_abejorral = Municipio.objects.create(
            codigo_dane="05002",
            departamento=self.departamento,
            nombre="ABEJORRAL",
        )

        self.user1 = CustomUser.objects.create(
            username="cliente1",
            email="cliente1@test.com",
            password=SECURE_PASSWORD_HASH,
            role=CustomUser.Roles.CLIENTE,
            is_active=True
        )

        self.user2 = CustomUser.objects.create(
            username="cliente2",
            email="cliente2@test.com",
            password=SECURE_PASSWORD_HASH,
            role=CustomUser.Roles.CLIENTE,
            is_active=True
        )

        self.ubicacion_user2 = Ubicacion.objects.create(
            usuario=self.user2,
            municipio=self.municipio_medellin,
            name="Casa Cliente 2",
            street="Calle Falsa 123",
            phone="+57 300 000 0000",
            postalCode="050022"
        )

    async def _get_auth_headers(self, username: str, password: str = SECURE_PASSWORD) -> dict:
        user = await CustomUser.objects.aget(username=username)
        token = create_jwt_for_user(user, expires_in=86400)
        return {"authorization": f"Bearer {token}"}

    async def test_listar_departamentos(self):
        async with AsyncTestClient(api) as client:
            response = await client.get("/api/ubicaciones/departamentos")
            self.assertEqual(response.status_code, 200)
            data = response.json()

            self.assertTrue(any(d["codigo_dane"] == "05" for d in data))

    async def test_listar_municipios(self):
        async with AsyncTestClient(api) as client:
            response = await client.get("/api/ubicaciones/departamentos/05/municipios")
            self.assertEqual(response.status_code, 200)
            data = response.json()

            medellin = next(m for m in data if m["codigo_dane"] == "05001")
            self.assertEqual(medellin["nombre"], "MEDELLIN")
            self.assertEqual(medellin["departamento_id"], "05")

    async def test_crear_ubicacion_usuario(self):
        headers = await self._get_auth_headers("cliente1", "secure123")
        payload = {
            "municipio_id": "05001",
            "name": "Oficina Principal",
            "street": "Cra 43A # 1-50",
            "phone": "+57 321 123 4567",
        }

        async with AsyncTestClient(api) as client:
            response = await client.post(
                "/api/ubicaciones/mis-direcciones",
                json=payload,
                headers=headers,
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()

            self.assertEqual(data["name"], "Oficina Principal")
            self.assertEqual(data["municipio_id"], "05001")
            self.assertEqual(data["city"], "MEDELLIN")
            self.assertEqual(data["state"], "Antioquia")
            self.assertEqual(data["country"], "CO")

            ubicaciones_qty = await Ubicacion.objects.filter(usuario=self.user1).acount()
            self.assertEqual(ubicaciones_qty, 1)

    async def test_usuario_puede_tener_multiples_ubicaciones(self):
        headers = await self._get_auth_headers("cliente1", "secure123")

        async with AsyncTestClient(api) as client:
            first_response = await client.post(
                "/api/ubicaciones/mis-direcciones",
                json={
                    "municipio_id": "05001",
                    "name": "Casa",
                    "street": "Calle 1",
                    "phone": "3001111111",
                },
                headers=headers,
            )
            second_response = await client.post(
                "/api/ubicaciones/mis-direcciones",
                json={
                    "municipio_id": "05002",
                    "name": "Oficina",
                    "street": "Carrera 2",
                    "phone": "3002222222",
                },
                headers=headers,
            )

            self.assertEqual(first_response.status_code, 200)
            self.assertEqual(second_response.status_code, 200)

            list_response = await client.get(
                "/api/ubicaciones/mis-direcciones",
                headers=headers,
            )

        self.assertEqual(list_response.status_code, 200)
        data = list_response.json()
        self.assertEqual(len(data), 2)

    async def test_listar_mis_ubicaciones(self):
        headers = await self._get_auth_headers("cliente1", "secure123")

        qty_before = await Ubicacion.objects.filter(usuario=self.user1).acount()
        self.assertEqual(qty_before, 0)

        await Ubicacion.objects.acreate(
            usuario_id=self.user1.id,
            municipio_id="05001",
            name="Bodega",
            street="Otra calle",
            phone="300"
        )

        async with AsyncTestClient(api) as client:
            response = await client.get(
                "/api/ubicaciones/mis-direcciones",
                headers=headers,
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "Bodega")

    async def test_eliminar_ubicacion_propia(self):
        headers = await self._get_auth_headers("cliente2", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.delete(
                f"/api/ubicaciones/mis-direcciones/{self.ubicacion_user2.id}",
                headers=headers,
            )
            self.assertEqual(response.status_code, 200)

            exist = await Ubicacion.objects.filter(id=self.ubicacion_user2.id).aexists()
            self.assertFalse(exist)

    async def test_no_puedes_eliminar_ubicacion_ajena(self):
        headers = await self._get_auth_headers("cliente1", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.delete(
                f"/api/ubicaciones/mis-direcciones/{self.ubicacion_user2.id}",
                headers=headers,
            )
            self.assertEqual(response.status_code, 404)

    async def test_no_autenticado_no_puede_crear_ubicacion(self):
        async with AsyncTestClient(api) as client:
            response = await client.post(
                "/api/ubicaciones/mis-direcciones",
                json={
                    "municipio_id": "05001",
                    "name": "Casa",
                    "street": "Calle 5",
                    "phone": "3003333333",
                },
            )

        self.assertEqual(response.status_code, 401)

    async def test_no_puedes_crear_con_municipio_inexistente(self):
        headers = await self._get_auth_headers("cliente1", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.post(
                "/api/ubicaciones/mis-direcciones",
                json={
                    "municipio_id": "99999",
                    "name": "Casa",
                    "street": "Calle 5",
                    "phone": "3003333333",
                },
                headers=headers,
            )

        self.assertEqual(response.status_code, 404)

    async def test_no_hay_endpoint_para_mutar_ubicacion_existente(self):
        headers = await self._get_auth_headers("cliente2", "secure123")

        async with AsyncTestClient(api) as client:
            response = await client.patch(
                f"/api/ubicaciones/mis-direcciones/{self.ubicacion_user2.id}",
                json={"name": "Nombre Mutado"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 404)
