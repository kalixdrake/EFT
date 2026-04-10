from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiInventario.models import Producto
from apiUsuarios.models import Cliente, Empleado, Usuario


class Stage7InventarioHardeningTests(APITestCase):
    def setUp(self):
        external_group, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")
        admin_group, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")

        self.admin = Usuario.objects.create_user(username="stage7_inv_admin", password="pass1234")
        self.admin.groups.add(admin_group)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-S7-INV", salario_base=0)

        self.external = Usuario.objects.create_user(username="stage7_inv_external", password="pass1234")
        self.external.groups.add(external_group)
        Cliente.objects.create(usuario=self.external)

        self.producto = Producto.objects.create(
            nombre="Prod Stage 7",
            sku="STAGE7-INV-001",
            precio_base=10,
            stock_actual=2,
            stock_minimo=5,
            activo=True,
        )

    def test_externo_no_puede_ajustar_stock(self):
        self.client.force_authenticate(self.external)
        response = self.client.post(
            f"/api/productos/{self.producto.id}/ajustar_stock/",
            {"stock": 9, "motivo": "test"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_externo_puede_ver_bajo_stock_segun_grant_company(self):
        self.client.force_authenticate(self.external)
        response = self.client.get("/api/productos/bajo_stock/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["sku"], "STAGE7-INV-001")
