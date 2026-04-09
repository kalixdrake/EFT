from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apiUsuarios.models import Usuario, Empleado
from apiUbicaciones.models import Pais, Departamento, Ciudad, Ubicacion
from apiInventario.models import (
    Producto,
    MovimientoInventario,
    CategoriaActivo,
    ActivoFijo,
    DepreciacionActivo,
    MantenimientoActivo,
    MovimientoActivo,
)


class InventarioMovimientoTests(TestCase):
    def setUp(self):
        admin_group, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.admin = Usuario.objects.create_user(username="admin_inv", password="pass1234")
        self.admin.groups.add(admin_group)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-INV-1", salario_base=0)
        self.producto = Producto.objects.create(
            nombre="Producto Inv",
            sku="INV-001",
            precio_base=10,
            stock_actual=5,
            stock_minimo=1,
            activo=True,
        )

    def test_movimiento_salida_actualiza_stock(self):
        movimiento = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo="SALIDA",
            cantidad=2,
            usuario=self.admin,
            motivo="Prueba salida",
        )
        self.producto.refresh_from_db()
        self.assertEqual(movimiento.stock_anterior, 5)
        self.assertEqual(movimiento.stock_nuevo, 3)
        self.assertEqual(self.producto.stock_actual, 3)


class ActivosFijosTests(TestCase):
    def setUp(self):
        admin_group, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.admin = Usuario.objects.create_user(username="admin_assets", password="pass1234")
        self.admin.groups.add(admin_group)
        self.empleado = Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-ACT-1", salario_base=1000)
        self.otro_usuario = Usuario.objects.create_user(username="emp_assets_2", password="pass1234")
        self.otro_empleado = Empleado.objects.create(usuario=self.otro_usuario, numero_empleado="EMP-ACT-2", salario_base=1200)

        pais = Pais.objects.create(nombre="Venezuela", codigo_iso="VEN")
        dep = Departamento.objects.create(nombre="Distrito Capital", pais=pais)
        ciudad = Ciudad.objects.create(nombre="Caracas", departamento=dep)
        self.ubicacion = Ubicacion.objects.create(nombre="Sede Principal", direccion="Av Principal", ciudad=ciudad)
        self.ubicacion_2 = Ubicacion.objects.create(nombre="Deposito", direccion="Zona Industrial", ciudad=ciudad)

        self.categoria = CategoriaActivo.objects.create(
            nombre="Computadores",
            vida_util_meses=60,
            tasa_depreciacion_anual=20,
            activo=True,
        )
        self.activo = ActivoFijo.objects.create(
            codigo_activo="AF-001",
            nombre="Laptop Lenovo",
            tipo="COMPUTADOR",
            categoria=self.categoria,
            valor_compra=1200,
            valor_residual=200,
            asignado_a_empleado=self.empleado,
            asignado_a_ubicacion=self.ubicacion,
        )

    def test_depreciacion_lineal(self):
        dep = DepreciacionActivo.registrar_lineal(self.activo, timezone.now().date())
        self.assertIsNotNone(dep)
        self.assertEqual(dep.monto, self.activo.depreciacion_mensual_estimado())
        self.assertEqual(dep.valor_en_libros, self.activo.valor_compra - dep.monto)

    def test_movimiento_reasignacion_cambia_responsable(self):
        mov = MovimientoActivo.objects.create(
            activo=self.activo,
            tipo="REASIGNACION",
            responsable_nuevo=self.otro_empleado,
            usuario=self.admin,
            motivo="Cambio de responsable",
        )
        self.activo.refresh_from_db()
        self.assertEqual(mov.responsable_anterior, self.empleado)
        self.assertEqual(self.activo.asignado_a_empleado, self.otro_empleado)
        self.assertEqual(self.activo.estado, ActivoFijo.EstadoActivo.ASIGNADO)

    def test_mantenimiento_alerta_vencida(self):
        mant = MantenimientoActivo.objects.create(
            activo=self.activo,
            tipo="PREVENTIVO",
            estado="PENDIENTE",
            descripcion="Revisión general",
            fecha_programada=timezone.now().date() - timedelta(days=1),
        )
        self.assertTrue(mant.alerta_vencida)

    def test_movimiento_traslado_cambia_ubicacion(self):
        MovimientoActivo.objects.create(
            activo=self.activo,
            tipo="TRASLADO",
            ubicacion_nueva=self.ubicacion_2,
            usuario=self.admin,
            motivo="Traslado operativo",
        )
        self.activo.refresh_from_db()
        self.assertEqual(self.activo.asignado_a_ubicacion, self.ubicacion_2)
