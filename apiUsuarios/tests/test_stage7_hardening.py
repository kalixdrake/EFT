from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apiPedidos.models import Pedido
from apiUbicaciones.models import Ciudad, Departamento, Pais, Ubicacion
from apiUsuarios.models import Cliente, Empleado, Socio, Usuario
from apiTransacciones.models import Nomina


class Stage7EndpointHardeningTests(APITestCase):
    def setUp(self):
        self.group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")

        self.admin = Usuario.objects.create_user(username="stage7_admin", password="pass1234")
        self.admin.groups.add(self.group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-S7-ADM", salario_base=0)

        self.external_cliente_user = Usuario.objects.create_user(username="stage7_cliente_1", password="pass1234")
        self.external_cliente_user.groups.add(self.group_external)
        self.external_cliente = Cliente.objects.create(usuario=self.external_cliente_user)

        self.external_cliente_user_2 = Usuario.objects.create_user(username="stage7_cliente_2", password="pass1234")
        self.external_cliente_user_2.groups.add(self.group_external)
        self.external_cliente_2 = Cliente.objects.create(usuario=self.external_cliente_user_2)

        self.external_socio_user = Usuario.objects.create_user(username="stage7_socio", password="pass1234")
        self.external_socio_user.groups.add(self.group_external)
        self.external_socio = Socio.objects.create(usuario=self.external_socio_user, saldo_pendiente=Decimal("0.00"))

        pais = Pais.objects.create(nombre="Pais S7", codigo_iso="PS7")
        departamento = Departamento.objects.create(nombre="Depto S7", pais=pais)
        ciudad = Ciudad.objects.create(nombre="Ciudad S7", departamento=departamento)
        self.ubicacion = Ubicacion.objects.create(nombre="Ubicacion S7", direccion="Dir S7", ciudad=ciudad)

        self.pedido = Pedido.objects.create(
            tipo=Pedido.TipoPedido.VENTA_CLIENTE,
            estado=Pedido.EstadoPedido.PENDIENTE,
            cliente=self.external_cliente_user,
            interno_asignado=self.admin,
            ubicacion_entrega=self.ubicacion,
        )

        self.nomina = Nomina.objects.create(
            empleado=self.admin,
            salario_base=Decimal("1000.00"),
            periodicidad=Nomina.Periodicidad.MENSUAL,
            bonos=Decimal("0.00"),
            deducciones=Decimal("0.00"),
            periodo_inicio=timezone.now().date() - timedelta(days=15),
            periodo_fin=timezone.now().date(),
            fecha_pago_programada=timezone.now().date(),
            estado=Nomina.EstadoPago.PENDIENTE,
        )

    def test_cliente_lista_clientes_filtrado_por_scope_own(self):
        self.client.force_authenticate(self.external_cliente_user)
        response = self.client.get("/api/clientes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["usuario"], self.external_cliente_user.id)

    def test_socio_externo_no_puede_ajustar_saldo(self):
        self.client.force_authenticate(self.external_socio_user)
        response = self.client.post(
            f"/api/socios/{self.external_socio.id}/ajustar_saldo/",
            {"monto": "10.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_externo_no_puede_cambiar_estado_pedido(self):
        self.client.force_authenticate(self.external_cliente_user)
        response = self.client.post(
            f"/api/pedidos/{self.pedido.id}/cambiar_estado/",
            {"estado": Pedido.EstadoPedido.CANCELADO},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_externo_no_puede_ver_nominas_pendientes(self):
        self.client.force_authenticate(self.external_cliente_user)
        response = self.client.get("/api/nominas/pendientes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

