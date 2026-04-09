from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apiInventario.models import Producto
from apiUsuarios.models import Usuario, Empleado

from .models import Impuesto, ReglaImpuesto, AsignacionImpuesto, SnapshotImpuestoTransaccional
from .services import calcular_impuestos_y_snapshots


class ImpuestosServiceTests(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Producto Test",
            sku="TEST-IMP-001",
            precio_base=Decimal("100.00"),
            stock_actual=10,
            stock_minimo=1,
            activo=True,
        )
        self.usuario = Usuario.objects.create_user(username="emp_imp", password="pass1234")
        self.empleado = Empleado.objects.create(
            usuario=self.usuario,
            numero_empleado="EMP-IMP-001",
            salario_base=Decimal("1000.00"),
        )
        hoy = timezone.now().date()
        self.impuesto_iva = Impuesto.objects.create(
            nombre="IVA 16",
            codigo="IVA16",
            tipo_impuesto="IVA",
            tipo_calculo="PERCENTAGE",
            tasa=Decimal("16.00"),
        )
        self.impuesto_recargo = Impuesto.objects.create(
            nombre="Recargo fijo",
            codigo="FIX10",
            tipo_impuesto="OTRO",
            tipo_calculo="FIXED",
            monto_fijo=Decimal("10.00"),
        )
        self.regla_producto = ReglaImpuesto.objects.create(
            impuesto=self.impuesto_iva,
            tipo_sujeto="PRODUCTO",
            base_imponible="SUBTOTAL",
            prioridad=10,
            acumulable=False,
            fecha_inicio=hoy - timedelta(days=1),
            fecha_fin=hoy + timedelta(days=30),
        )
        self.regla_producto2 = ReglaImpuesto.objects.create(
            impuesto=self.impuesto_recargo,
            tipo_sujeto="PRODUCTO",
            base_imponible="TOTAL_ACTUAL",
            prioridad=20,
            acumulable=True,
            fecha_inicio=hoy - timedelta(days=1),
            fecha_fin=hoy + timedelta(days=30),
        )
        self.regla_empleado = ReglaImpuesto.objects.create(
            impuesto=self.impuesto_iva,
            tipo_sujeto="EMPLEADO",
            base_imponible="SALARIO_BASE",
            prioridad=10,
            acumulable=False,
            fecha_inicio=hoy - timedelta(days=1),
            fecha_fin=hoy + timedelta(days=30),
        )
        AsignacionImpuesto.objects.create(
            regla=self.regla_producto,
            ambito="PRODUCTO",
            producto=self.producto,
            prioridad_local=10,
        )
        AsignacionImpuesto.objects.create(
            regla=self.regla_producto2,
            ambito="PRODUCTO",
            producto=self.producto,
            prioridad_local=20,
        )
        AsignacionImpuesto.objects.create(
            regla=self.regla_empleado,
            ambito="EMPLEADO",
            empleado=self.empleado,
            prioridad_local=10,
        )

    def test_producto_taxes_with_priority_and_accumulation(self):
        total_impuestos = calcular_impuestos_y_snapshots(
            origen="PEDIDO_DETALLE",
            origen_id=99,
            tipo_sujeto="PRODUCTO",
            subtotal=Decimal("100.00"),
            descuento_pct=Decimal("0"),
            producto=self.producto,
        )
        self.assertEqual(total_impuestos, Decimal("26.00"))
        self.assertEqual(
            SnapshotImpuestoTransaccional.objects.filter(origen="PEDIDO_DETALLE", origen_id=99).count(),
            2,
        )

    def test_empleado_taxes_from_salary(self):
        total_impuestos = calcular_impuestos_y_snapshots(
            origen="EMPLEADO_CONCEPTO",
            origen_id=7,
            tipo_sujeto="EMPLEADO",
            subtotal=Decimal("0.00"),
            empleado=self.empleado,
            monto_explicito=Decimal("0.00"),
        )
        self.assertEqual(total_impuestos, Decimal("160.00"))
        snapshot = SnapshotImpuestoTransaccional.objects.get(origen="EMPLEADO_CONCEPTO", origen_id=7)
        self.assertEqual(snapshot.base_imponible, Decimal("1000.00"))

