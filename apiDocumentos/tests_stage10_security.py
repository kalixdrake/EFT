from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from apiUsuarios.models import Cliente, Empleado, Usuario

from .models import Documento, TipoDocumento


class Stage10DocumentosSecurityTests(APITestCase):
    def setUp(self):
        self.group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")

        self.admin = Usuario.objects.create_user(username="stage10_doc_admin", password="pass1234")
        self.admin.groups.add(self.group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-S10-DOC-ADM", salario_base=0)

        self.cliente_a_user = Usuario.objects.create_user(username="stage10_doc_cli_a", password="pass1234")
        self.cliente_a_user.groups.add(self.group_external)
        self.cliente_a = Cliente.objects.create(usuario=self.cliente_a_user)

        self.cliente_b_user = Usuario.objects.create_user(username="stage10_doc_cli_b", password="pass1234")
        self.cliente_b_user.groups.add(self.group_external)
        self.cliente_b = Cliente.objects.create(usuario=self.cliente_b_user)

        self.tipo_cliente = TipoDocumento.objects.create(
            codigo="DOC-S10-CLI",
            nombre="Documento Cliente S10",
            propietario_permitido=TipoDocumento.TipoPropietario.CLIENTE,
            requiere_vencimiento=False,
            activo=True,
        )

        self.doc_cliente_b = Documento.objects.create(
            codigo="DOC-S10-B",
            tipo_documento=self.tipo_cliente,
            titulo="Doc de cliente B",
            estado=Documento.EstadoDocumento.PUBLICADO,
            archivo_actual=SimpleUploadedFile("b.txt", b"doc-b", content_type="text/plain"),
            propietario_cliente=self.cliente_b,
            usuario_creador=self.admin,
            usuario_actualizador=self.admin,
        )

    def test_cliente_a_no_puede_ver_documento_cliente_b(self):
        self.client.force_authenticate(self.cliente_a_user)
        response = self.client.get(f"/api/documentos/{self.doc_cliente_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_a_no_puede_descargar_documento_cliente_b(self):
        self.client.force_authenticate(self.cliente_a_user)
        response = self.client.get(f"/api/documentos/{self.doc_cliente_b.id}/descargar/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
