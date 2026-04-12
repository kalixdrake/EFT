from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apiCuentas.models.cuenta_model import Cuenta
from apiTransacciones.models import Categoria, ProgramacionTransaccion
from apiUsuarios.models import Cliente, Empleado, Usuario


class Stage7TransaccionesHardeningTests(APITestCase):
    fixtures = [
        "json/init_bancos.json",
        "json/init_cuentas.json",
        "json/init_categorias_transacciones.json",
    ]

    def setUp(self):
        self.group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")

        self.admin = Usuario.objects.create_user(username="stage7_tx_admin", password="pass1234")
        self.admin.groups.add(self.group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-S7-TX", salario_base=0)

        self.external = Usuario.objects.create_user(username="stage7_tx_external", password="pass1234")
        self.external.groups.add(self.group_external)
        Cliente.objects.create(usuario=self.external)

        self.cuenta_origen = Cuenta.objects.get(id=1)
        self.cuenta_destino = Cuenta.objects.get(id=2)
        self.categoria_egreso = Categoria.objects.get(id=3)

        self.programacion = ProgramacionTransaccion.objects.create(
            monto=Decimal("10.00"),
            descripcion="Programacion Stage 7",
            fecha_programada=timezone.now() + timedelta(days=1),
            categoria=self.categoria_egreso,
            cuenta=self.cuenta_origen,
            estado="PENDIENTE",
            frecuencia="UNICA",
            activa=True,
        )

    def test_usuario_externo_no_puede_transferir(self):
        self.client.force_authenticate(self.external)
        response = self.client.post(
            "/api/transacciones/transferir/",
            {
                "cuenta_origen": self.cuenta_origen.id,
                "cuenta_destino": self.cuenta_destino.id,
                "monto": "1.00",
                "descripcion": "Intento no autorizado",
                "fecha_ejecucion": timezone.now().isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_externo_no_puede_ver_programaciones_pendientes(self):
        self.client.force_authenticate(self.external)
        response = self.client.get("/api/programaciones/pendientes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
