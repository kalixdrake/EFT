from decimal import Decimal

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiInventario.models import Producto
from apiPedidos.models import Pedido
from apiUbicaciones.models import Ciudad, Departamento, Pais, Ubicacion
from apiUsuarios.models import Cliente, Empleado, Socio, Usuario


class Stage10PedidosSecurityTests(APITestCase):
    def setUp(self):
        self.group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.group_logistica, _ = Group.objects.get_or_create(name="LOGISTICA")
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")

        self.admin = Usuario.objects.create_user(username="stage10_ped_admin", password="pass1234")
        self.admin.groups.add(self.group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-S10-PED-ADM", salario_base=0)

        self.logistica = Usuario.objects.create_user(username="stage10_ped_log", password="pass1234")
        self.logistica.groups.add(self.group_logistica)
        Empleado.objects.create(usuario=self.logistica, numero_empleado="EMP-S10-PED-LOG", salario_base=0)

        self.cliente_a_user = Usuario.objects.create_user(username="stage10_ped_cli_a", password="pass1234")
        self.cliente_a_user.groups.add(self.group_external)
        self.cliente_a = Cliente.objects.create(usuario=self.cliente_a_user)

        self.cliente_b_user = Usuario.objects.create_user(username="stage10_ped_cli_b", password="pass1234")
        self.cliente_b_user.groups.add(self.group_external)
        self.cliente_b = Cliente.objects.create(usuario=self.cliente_b_user)

        self.socio_user = Usuario.objects.create_user(username="stage10_ped_socio", password="pass1234")
        self.socio_user.groups.add(self.group_external)
        self.socio = Socio.objects.create(usuario=self.socio_user, saldo_pendiente=Decimal("0.00"))

        pais = Pais.objects.create(nombre="Pais S10 PED", codigo_iso="S10P")
        departamento = Departamento.objects.create(nombre="Depto S10 PED", pais=pais)
        ciudad = Ciudad.objects.create(nombre="Ciudad S10 PED", departamento=departamento)
        self.ubicacion = Ubicacion.objects.create(nombre="Ubicacion S10 PED", direccion="Dir S10 PED", ciudad=ciudad)

        self.producto = Producto.objects.create(
            nombre="Prod S10 PED",
            sku="S10-PED-001",
            precio_base=Decimal("25.00"),
            stock_actual=30,
            stock_minimo=2,
            activo=True,
        )

        self.pedido_cliente_b = Pedido.objects.create(
            tipo=Pedido.TipoPedido.VENTA_CLIENTE,
            estado=Pedido.EstadoPedido.PENDIENTE,
            cliente=self.cliente_b_user,
            interno_asignado=self.admin,
            ubicacion_entrega=self.ubicacion,
        )
        self.pedido_socio = Pedido.objects.create(
            tipo=Pedido.TipoPedido.APARTADO_SOCIO,
            estado=Pedido.EstadoPedido.PENDIENTE_APROBACION,
            cliente=self.socio_user,
            interno_asignado=self.admin,
            ubicacion_entrega=self.ubicacion,
        )

    def test_cliente_a_no_puede_ver_detalle_pedido_cliente_b(self):
        self.client.force_authenticate(self.cliente_a_user)
        response = self.client.get(f"/api/pedidos/{self.pedido_cliente_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_logistica_no_puede_aprobar_pedido(self):
        self.client.force_authenticate(self.logistica)
        response = self.client.post(f"/api/pedidos/{self.pedido_socio.id}/aprobar/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_no_puede_crear_pedido_para_otro_usuario(self):
        self.client.force_authenticate(self.cliente_a_user)
        response = self.client.post(
            "/api/pedidos/",
            {
                "tipo": Pedido.TipoPedido.VENTA_CLIENTE,
                "cliente": self.cliente_b_user.id,
                "ubicacion_entrega": self.ubicacion.id,
                "detalles": [
                    {
                        "producto": self.producto.id,
                        "cantidad": 1,
                        "precio_unitario": "25.00",
                    }
                ],
                "notas": "Intento lateral",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cliente", response.data)
