from decimal import Decimal
from datetime import timedelta

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from apiUsuarios.models import Usuario, Cliente, Empleado
from apiInventario.models import Producto
from apiUbicaciones.models import Pais, Departamento, Ciudad, Ubicacion
from apiImpuestos.models import Impuesto, ReglaImpuesto, AsignacionImpuesto, SnapshotImpuestoTransaccional
from apiPedidos.models import Pedido, DetallePedido


class PedidoImpuestosIntegrationTests(TestCase):
    def setUp(self):
        admin_group, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.admin = Usuario.objects.create_user(username="admin_pedido_imp", password="pass1234")
        self.admin.groups.add(admin_group)
        self.empleado = Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-PED-IMP-1", salario_base=0)

        self.cliente_user = Usuario.objects.create_user(username="cliente_pedido_imp", password="pass1234")
        Cliente.objects.create(usuario=self.cliente_user)

        pais = Pais.objects.create(nombre="Venezuela", codigo_iso="VEN")
        dep = Departamento.objects.create(nombre="Miranda", pais=pais)
        ciudad = Ciudad.objects.create(nombre="Caracas", departamento=dep)
        self.ubicacion = Ubicacion.objects.create(nombre="Oficina Central", direccion="Av. 1", ciudad=ciudad)

        self.producto = Producto.objects.create(
            nombre="Producto A",
            sku="PROD-IMP-001",
            precio_base=Decimal("100.00"),
            stock_actual=50,
            stock_minimo=5,
            activo=True,
        )

        hoy = timezone.now().date()
        iva = Impuesto.objects.create(
            nombre="IVA 16",
            codigo="IVA16-PED",
            tipo_impuesto="IVA",
            tipo_calculo="PERCENTAGE",
            tasa=Decimal("16.00"),
        )
        regla = ReglaImpuesto.objects.create(
            impuesto=iva,
            tipo_sujeto="PRODUCTO",
            base_imponible="SUBTOTAL",
            prioridad=10,
            acumulable=False,
            fecha_inicio=hoy - timedelta(days=1),
            fecha_fin=hoy + timedelta(days=10),
        )
        AsignacionImpuesto.objects.create(
            regla=regla,
            ambito="PRODUCTO",
            producto=self.producto,
            prioridad_local=10,
        )

    def test_detalle_pedido_calcula_impuesto_y_snapshot(self):
        pedido = Pedido.objects.create(
            tipo="VENTA_CLIENTE",
            estado="PENDIENTE",
            cliente=self.cliente_user,
            interno_asignado=self.admin,
            ubicacion_entrega=self.ubicacion,
        )
        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=self.producto,
            cantidad=2,
            precio_unitario=Decimal("100.00"),
        )
        detalle.refresh_from_db()
        pedido.refresh_from_db()

        self.assertEqual(detalle.monto_impuesto, Decimal("32.00"))
        self.assertEqual(pedido.total, Decimal("232.00"))
        self.assertTrue(
            SnapshotImpuestoTransaccional.objects.filter(
                origen="PEDIDO_DETALLE",
                origen_id=detalle.id,
            ).exists()
        )
