from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from apiAuditoria.models import EventoAuditoria
from apiDocumentos.models import Documento, TipoDocumento, VersionDocumento
from apiUsuarios.models import Cliente, Empleado, Usuario


class AuditoriaTransversalTests(APITestCase):
    def setUp(self):
        group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        group_auditor, _ = Group.objects.get_or_create(name="AUDITOR")
        group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")

        self.admin = Usuario.objects.create_user(username="audit_admin", password="pass1234")
        self.admin.groups.add(group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-AUD-1", salario_base=0)

        self.auditor = Usuario.objects.create_user(username="audit_reader", password="pass1234")
        self.auditor.groups.add(group_auditor)
        Empleado.objects.create(usuario=self.auditor, numero_empleado="EMP-AUD-2", salario_base=0)

        self.external = Usuario.objects.create_user(username="audit_external", password="pass1234")
        self.external.groups.add(group_external)
        self.external_cliente = Cliente.objects.create(usuario=self.external)

        self.tipo_doc = TipoDocumento.objects.create(
            codigo="AUD-DOC",
            nombre="Documento Auditable",
            propietario_permitido=TipoDocumento.TipoPropietario.CLIENTE,
            requiere_vencimiento=False,
            activo=True,
        )
        file1 = SimpleUploadedFile("audit.txt", b"audit", content_type="text/plain")
        self.documento = Documento.objects.create(
            codigo="AUD-001",
            tipo_documento=self.tipo_doc,
            titulo="Doc audit",
            estado=Documento.EstadoDocumento.PUBLICADO,
            archivo_actual=file1,
            propietario_cliente=self.external_cliente,
            usuario_creador=self.admin,
            usuario_actualizador=self.admin,
        )
        VersionDocumento.objects.create(
            documento=self.documento,
            numero_version=1,
            archivo=self.documento.archivo_actual,
            observaciones="init",
            usuario_editor=self.admin,
        )

    def test_registra_evento_en_acceso_documento(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(f"/api/documentos/{self.documento.id}/visualizar/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        evento = EventoAuditoria.objects.filter(endpoint=f"/api/documentos/{self.documento.id}/visualizar/").first()
        self.assertIsNotNone(evento)
        self.assertEqual(evento.usuario, self.admin)
        self.assertEqual(evento.recurso, "documento")
        self.assertEqual(evento.accion, "visualizar")
        self.assertEqual(evento.resultado, EventoAuditoria.ResultadoEvento.SUCCESS)

    def test_registra_forbidden_en_endpoint_critico(self):
        self.client.force_authenticate(self.external)
        response = self.client.get("/api/nominas/pendientes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        evento = EventoAuditoria.objects.filter(endpoint="/api/nominas/pendientes/").first()
        self.assertIsNotNone(evento)
        self.assertEqual(evento.resultado, EventoAuditoria.ResultadoEvento.FORBIDDEN)
        self.assertEqual(evento.codigo_estado, status.HTTP_403_FORBIDDEN)

    def test_endpoint_auditoria_visible_para_auditor(self):
        EventoAuditoria.objects.create(
            usuario=self.admin,
            endpoint="/api/pedidos/",
            metodo_http="GET",
            accion="list",
            recurso="pedido",
            resultado=EventoAuditoria.ResultadoEvento.SUCCESS,
            codigo_estado=200,
            metadata={"seed": True},
        )
        self.client.force_authenticate(self.auditor)
        response = self.client.get("/api/auditoria-eventos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

