from decimal import Decimal

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiCuentas.models.cuenta_model import Cuenta
from apiTransacciones.models import Categoria, Nomina
from apiUsuarios.models import Cliente, Empleado, Usuario


class Stage10TransaccionesSecurityTests(APITestCase):
    fixtures = [
        "json/init_bancos.json",
        "json/init_cuentas.json",
        "json/init_categorias_transacciones.json",
    ]

    def setUp(self):
        self.group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.group_auditor, _ = Group.objects.get_or_create(name="AUDITOR")
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")

        self.admin = Usuario.objects.create_user(username="stage10_tx_admin", password="pass1234")
        self.admin.groups.add(self.group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-S10-TX-ADM", salario_base=0)

        self.auditor = Usuario.objects.create_user(username="stage10_tx_aud", password="pass1234")
        self.auditor.groups.add(self.group_auditor)
        Empleado.objects.create(usuario=self.auditor, numero_empleado="EMP-S10-TX-AUD", salario_base=0)

        self.external = Usuario.objects.create_user(username="stage10_tx_external", password="pass1234")
        self.external.groups.add(self.group_external)
        Cliente.objects.create(usuario=self.external)

        self.cuenta_origen = Cuenta.objects.get(id=1)
        self.cuenta_destino = Cuenta.objects.get(id=2)
        self.categoria = Categoria.objects.get(id=3)

    def test_auditor_no_puede_crear_transaccion(self):
        self.client.force_authenticate(self.auditor)
        response = self.client.post(
            "/api/transacciones/",
            {
                "monto": "100.00",
                "descripcion": "Intento auditor",
                "categoria": self.categoria.id,
                "cuenta": self.cuenta_origen.id,
                "fecha_ejecucion": "2026-01-01T00:00:00Z",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auditor_no_puede_transferir(self):
        self.client.force_authenticate(self.auditor)
        response = self.client.post(
            "/api/transacciones/transferir/",
            {
                "cuenta_origen": self.cuenta_origen.id,
                "cuenta_destino": self.cuenta_destino.id,
                "monto": "10.00",
                "descripcion": "Intento transferencia auditor",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_externo_no_puede_crear_nomina(self):
        self.client.force_authenticate(self.external)
        response = self.client.post(
            "/api/nominas/",
            {
                "empleado": self.admin.id,
                "salario_base": "1000.00",
                "periodicidad": Nomina.Periodicidad.MENSUAL,
                "bonos": "0.00",
                "deducciones": "0.00",
                "periodo_inicio": "2026-01-01",
                "periodo_fin": "2026-01-31",
                "fecha_pago_programada": "2026-02-01",
                "estado": Nomina.EstadoPago.PENDIENTE,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
