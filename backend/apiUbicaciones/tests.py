from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiUbicaciones.models import Ciudad, ClienteUbicacion, Departamento, Pais, Ubicacion
from apiUsuarios.models import Cliente, Empleado, Socio, Usuario


class UbicacionesStage3Tests(APITestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username="ubic_admin",
            password="pass1234",
        )
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-UBIC-1", salario_base=0)
        admin_group, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.admin.groups.add(admin_group)
        self.cliente_user = Usuario.objects.create_user(username="ubic_cliente", password="pass1234")
        self.socio_user = Usuario.objects.create_user(username="ubic_socio", password="pass1234")
        self.cliente = Cliente.objects.create(usuario=self.cliente_user)
        self.socio = Socio.objects.create(usuario=self.socio_user)

        self.pais = Pais.objects.create(nombre="Colombia", codigo_iso="COL")
        self.depto = Departamento.objects.create(pais=self.pais, nombre="Cundinamarca", codigo="CUN")
        self.ciudad = Ciudad.objects.create(departamento=self.depto, nombre="Bogota", codigo_postal="110111")
        self.ubicacion = Ubicacion.objects.create(
            ciudad=self.ciudad,
            nombre="Bodega Norte",
            direccion="Calle 100 # 10-20",
            tipo=Ubicacion.Tipo.OPERATIVA,
        )
        self.client.force_authenticate(user=self.admin)

    def test_crud_ubicacion(self):
        resp_list = self.client.get("/api/ubicaciones/")
        self.assertEqual(resp_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_list.data), 1)

        resp_create = self.client.post(
            "/api/ubicaciones/",
            {
                "ciudad": self.ciudad.id,
                "nombre": "Oficina Centro",
                "direccion": "Carrera 7 # 20-10",
                "tipo": "ENTREGA",
            },
            format="json",
        )
        self.assertEqual(resp_create.status_code, status.HTTP_201_CREATED)
        created_id = resp_create.data["id"]

        resp_patch = self.client.patch(
            f"/api/ubicaciones/{created_id}/",
            {"referencia": "Piso 2"},
            format="json",
        )
        self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_patch.data["referencia"], "Piso 2")

    def test_filters_by_hierarchy(self):
        resp = self.client.get(f"/api/ubicaciones/?ciudad__departamento__pais={self.pais.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_cliente_ubicacion_single_principal_rule(self):
        ClienteUbicacion.objects.create(cliente=self.cliente, ubicacion=self.ubicacion, es_principal=True)
        with self.assertRaises(ValidationError):
            ClienteUbicacion.objects.create(cliente=self.cliente, ubicacion=self.ubicacion, es_principal=True)

    def test_relations_for_socio_and_empleado(self):
        empleado_user = Usuario.objects.create_user(username="ubic_emp", password="pass1234")
        empleado = Empleado.objects.create(usuario=empleado_user, numero_empleado="EMP-UBIC-2", salario_base=0)

        resp_socio = self.client.post(
            "/api/socios-ubicaciones/",
            {"socio": self.socio.id, "ubicacion": self.ubicacion.id, "es_principal": True},
            format="json",
        )
        self.assertEqual(resp_socio.status_code, status.HTTP_201_CREATED)

        resp_empleado = self.client.post(
            "/api/empleados-ubicaciones/",
            {"empleado": empleado.id, "ubicacion": self.ubicacion.id, "es_principal": True},
            format="json",
        )
        self.assertEqual(resp_empleado.status_code, status.HTTP_201_CREATED)
