from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import Group
from apiBancos.models.banco_model import Banco
from apiUsuarios.models import Empleado, Usuario

class BancoViewSetTest(APITestCase):
    fixtures = ["json/init_bancos.json"]

    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="bancos_test_admin",
            password="pass1234",
        )
        Empleado.objects.create(usuario=self.user, numero_empleado=f"EMP-{self.user.id}", salario_base=0)
        admin_group, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.user.groups.add(admin_group)
        self.client.force_authenticate(user=self.user)

    def test_listar_bancos(self):
        url = reverse("banco-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["nombre"], "Banco Caja Social")

    def test_creacion_banco(self):
        """Verifica que podamos crear un banco correctamente con atributos válidos"""
        url = reverse("banco-list")
        data = {"nombre": "Banco Secundario"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Banco.objects.filter(nombre="Banco Secundario").exists())

