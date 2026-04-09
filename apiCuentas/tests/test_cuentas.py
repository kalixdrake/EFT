from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import Group
from apiCuentas.models.cuenta_model import Cuenta
from apiUsuarios.models import Empleado, Usuario

class CuentaViewSetTest(APITestCase):
    fixtures = ["json/init_bancos.json", "json/init_cuentas.json"]

    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="cuentas_test_admin",
            password="pass1234",
        )
        Empleado.objects.create(usuario=self.user, numero_empleado=f"EMP-{self.user.id}", salario_base=0)
        admin_group, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.user.groups.add(admin_group)
        self.client.force_authenticate(user=self.user)

    def test_leer_cuenta_existente(self):
        url = reverse("cuenta-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificamos que el fixture trajo el saldo correcto de 1000
        self.assertEqual(float(response.data[0]["saldo"]), 100000.0)

    def test_crear_cuenta_asociada_correctamente(self):
        """Verificamos la creación de una cuenta y que su banco exista"""
        url = reverse("cuenta-list")
        data = {"banco": 1, "saldo": 500.5}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cuenta = Cuenta.objects.get(id=res.data["id"])
        self.assertEqual(float(cuenta.saldo), 500.5)

