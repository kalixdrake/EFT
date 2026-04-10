from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apiUsuarios.models import Cliente, Empleado, Usuario

from .models import AccesoDocumento, Documento, TipoDocumento, VersionDocumento


class DocumentoApiTests(APITestCase):
    def setUp(self):
        admin_group, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        external_group, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")

        self.admin_user = Usuario.objects.create_user(username="admin_docs", password="pass1234")
        self.admin_user.groups.add(admin_group)
        self.admin_emp = Empleado.objects.create(
            usuario=self.admin_user,
            numero_empleado="EMP-DOC-1",
            salario_base=0,
        )

        self.cliente_user = Usuario.objects.create_user(username="cliente_docs", password="pass1234")
        self.cliente_user.groups.add(external_group)
        self.cliente = Cliente.objects.create(usuario=self.cliente_user)

        self.tipo_cliente = TipoDocumento.objects.create(
            codigo="DOC-ID-CLI",
            nombre="Identificacion Cliente",
            propietario_permitido=TipoDocumento.TipoPropietario.CLIENTE,
            requiere_vencimiento=True,
            dias_alerta_vencimiento=10,
        )
        self.tipo_empresa = TipoDocumento.objects.create(
            codigo="DOC-CORP",
            nombre="Documento Corporativo",
            propietario_permitido=TipoDocumento.TipoPropietario.EMPRESA,
            requiere_vencimiento=False,
        )

    def _file(self, name="archivo.txt", content=b"contenido"):
        return SimpleUploadedFile(name, content, content_type="text/plain")

    def test_documento_creacion_genera_version_inicial(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(
            reverse("documento-list"),
            {
                "codigo": "DOC-001",
                "tipo_documento": self.tipo_empresa.id,
                "titulo": "Manual interno",
                "descripcion": "Version inicial",
                "estado": Documento.EstadoDocumento.PUBLICADO,
                "archivo_actual": self._file(),
                "propietario_empresa": True,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        documento = Documento.objects.get(codigo="DOC-001")
        self.assertEqual(documento.ultima_version, 1)
        self.assertEqual(VersionDocumento.objects.filter(documento=documento).count(), 1)

    def test_documento_update_archivo_crea_nueva_version(self):
        self.client.force_authenticate(self.admin_user)
        documento = Documento.objects.create(
            codigo="DOC-002",
            tipo_documento=self.tipo_empresa,
            titulo="Politica",
            estado=Documento.EstadoDocumento.PUBLICADO,
            archivo_actual=self._file("v1.txt", b"v1"),
            propietario_empresa=True,
            usuario_creador=self.admin_user,
            usuario_actualizador=self.admin_user,
        )
        VersionDocumento.objects.create(
            documento=documento,
            numero_version=1,
            archivo=documento.archivo_actual,
            usuario_editor=self.admin_user,
            observaciones="init",
        )

        response = self.client.patch(
            reverse("documento-detail", args=[documento.id]),
            {"archivo_actual": self._file("v2.txt", b"v2")},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        documento.refresh_from_db()
        self.assertEqual(documento.ultima_version, 2)
        self.assertTrue(VersionDocumento.objects.filter(documento=documento, numero_version=2).exists())

    def test_usuario_externo_solo_ve_documentos_propios(self):
        Documento.objects.create(
            codigo="DOC-CLI-OK",
            tipo_documento=self.tipo_cliente,
            titulo="Contrato cliente",
            estado=Documento.EstadoDocumento.PUBLICADO,
            archivo_actual=self._file("cli.txt", b"cli"),
            fecha_vencimiento="2030-01-01",
            propietario_cliente=self.cliente,
            usuario_creador=self.admin_user,
            usuario_actualizador=self.admin_user,
        )
        Documento.objects.create(
            codigo="DOC-CORP-HIDDEN",
            tipo_documento=self.tipo_empresa,
            titulo="Solo internos",
            estado=Documento.EstadoDocumento.PUBLICADO,
            archivo_actual=self._file("corp.txt", b"corp"),
            propietario_empresa=True,
            usuario_creador=self.admin_user,
            usuario_actualizador=self.admin_user,
        )

        self.client.force_authenticate(self.cliente_user)
        response = self.client.get(reverse("documento-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codigos = {item["codigo"] for item in response.data}
        self.assertIn("DOC-CLI-OK", codigos)
        self.assertNotIn("DOC-CORP-HIDDEN", codigos)

    def test_descarga_y_visualizacion_generan_auditoria(self):
        documento = Documento.objects.create(
            codigo="DOC-003",
            tipo_documento=self.tipo_empresa,
            titulo="Procedimiento",
            estado=Documento.EstadoDocumento.PUBLICADO,
            archivo_actual=self._file("proc.txt", b"proc"),
            propietario_empresa=True,
            usuario_creador=self.admin_user,
            usuario_actualizador=self.admin_user,
        )
        VersionDocumento.objects.create(
            documento=documento,
            numero_version=1,
            archivo=documento.archivo_actual,
            usuario_editor=self.admin_user,
            observaciones="init",
        )

        self.client.force_authenticate(self.admin_user)
        ver_resp = self.client.get(reverse("documento-visualizar", args=[documento.id]))
        des_resp = self.client.get(reverse("documento-descargar", args=[documento.id]))
        self.assertEqual(ver_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(des_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(AccesoDocumento.objects.filter(documento=documento).count(), 2)
        self.assertTrue(
            AccesoDocumento.objects.filter(
                documento=documento, tipo_evento=AccesoDocumento.TipoEvento.VISUALIZACION
            ).exists()
        )
        self.assertTrue(
            AccesoDocumento.objects.filter(documento=documento, tipo_evento=AccesoDocumento.TipoEvento.DESCARGA).exists()
        )
