from unittest.mock import patch

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiInteracciones.models import InteraccionIA
from apiUsuarios.models import Cliente, Empleado, Usuario


class Stage10InteraccionesSecurityTests(APITestCase):
    def setUp(self):
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")
        self.group_contabilidad, _ = Group.objects.get_or_create(name="CONTABILIDAD")

        self.external = Usuario.objects.create_user(username="stage10_chat_external", password="pass1234")
        self.external.groups.add(self.group_external)
        Cliente.objects.create(usuario=self.external)

        self.accounting = Usuario.objects.create_user(username="stage10_chat_contabilidad", password="pass1234")
        self.accounting.groups.add(self.group_contabilidad)
        Empleado.objects.create(usuario=self.accounting, numero_empleado="EMP-S10-CHAT-CNT", salario_base=0)

    def test_chat_requires_authentication(self):
        response = self.client.post("/api/interacciones/chat/", {"prompt": "hola"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("apiInteracciones.views.interaccion_view.procesar_prompt_con_ia")
    def test_chat_rejects_user_without_capability(self, mock_ai):
        self.client.force_authenticate(self.external)
        mock_ai.return_value = {
            "ok": False,
            "error_code": "FORBIDDEN_CAPABILITY",
            "error": "No cuenta con capacidades para usar el chat IA.",
        }

        response = self.client.post("/api/interacciones/chat/", {"prompt": "quiero crear una transacción"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(InteraccionIA.objects.count(), 0)
        mock_ai.assert_called_once()

    @patch("apiInteracciones.views.interaccion_view.procesar_prompt_con_ia")
    def test_chat_allows_authorized_user_and_persists_interaction(self, mock_ai):
        self.client.force_authenticate(self.accounting)
        mock_ai.return_value = {
            "ok": True,
            "respuesta": "Puedes registrar la operación desde el módulo de finanzas.",
            "contexto": "Contexto de prueba",
            "roles": ["CONTABILIDAD"],
            "capabilities": [
                {"resource": "interaccion", "action": "create", "scope": "COMPANY"},
            ],
        }

        response = self.client.post("/api/interacciones/chat/", {"prompt": "¿puedo registrar egresos?"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("interaccion_id", response.data)
        self.assertEqual(InteraccionIA.objects.count(), 1)
        interaccion = InteraccionIA.objects.first()
        self.assertEqual(interaccion.usuario, self.accounting)
        self.assertTrue(interaccion.exitosa)
