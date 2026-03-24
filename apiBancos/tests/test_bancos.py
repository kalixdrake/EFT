from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apiBancos.models.banco_model import Banco

class BancoViewSetTest(APITestCase):
    fixtures = ["json/init_bancos.json"]

    def test_listar_bancos(self):
        url = reverse("banco-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nombre"], "Banco Central")

    def test_creacion_banco(self):
        """Verifica que podamos crear un banco correctamente con atributos válidos"""
        url = reverse("banco-list")
        data = {"nombre": "Banco Secundario"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Banco.objects.filter(nombre="Banco Secundario").exists())

