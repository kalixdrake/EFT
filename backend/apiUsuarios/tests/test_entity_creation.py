from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from decimal import Decimal
from datetime import timedelta

from django.utils import timezone

from apiUsuarios.models import Cliente, Empleado, Socio, Usuario
from apiImpuestos.models import Impuesto, ReglaImpuesto, AsignacionImpuesto, SnapshotImpuestoTransaccional
from apiImpuestos.services import calcular_impuestos_y_snapshots


class EntityCreationTests(APITestCase):
    def setUp(self):
        self.group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.admin = Usuario.objects.create_user(username="entity_admin", password="pass1234")
        self.admin.groups.add(self.group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-CRT-1", salario_base=0)
        self.client.force_authenticate(user=self.admin)

    def test_create_cliente_entity(self):
        response = self.client.post(
            "/api/usuarios/",
            {
                "username": "cliente_entity",
                "password": "pass1234",
                "password_confirm": "pass1234",
                "tipo_entidad": "CLIENTE",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = Usuario.objects.get(username="cliente_entity")
        self.assertTrue(Cliente.objects.filter(usuario=usuario).exists())

    def test_create_socio_entity(self):
        response = self.client.post(
            "/api/usuarios/",
            {
                "username": "socio_entity",
                "password": "pass1234",
                "password_confirm": "pass1234",
                "tipo_entidad": "SOCIO",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = Usuario.objects.get(username="socio_entity")
        self.assertTrue(Socio.objects.filter(usuario=usuario).exists())

    def test_create_empleado_entity(self):
        response = self.client.post(
            "/api/usuarios/",
            {
                "username": "empleado_entity",
                "password": "pass1234",
                "password_confirm": "pass1234",
                "tipo_entidad": "EMPLEADO",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = Usuario.objects.get(username="empleado_entity")
        self.assertTrue(Empleado.objects.filter(usuario=usuario).exists())

    def test_empleado_impuesto_concepto_laboral(self):
        empleado = Empleado.objects.get(usuario=self.admin)
        hoy = timezone.now().date()
        impuesto = Impuesto.objects.create(
            nombre="ISR Empleado",
            codigo="ISR-EMP-TST",
            tipo_impuesto="RETENCION",
            tipo_calculo="PERCENTAGE",
            tasa=Decimal("10.00"),
        )
        regla = ReglaImpuesto.objects.create(
            impuesto=impuesto,
            tipo_sujeto="EMPLEADO",
            base_imponible="SALARIO_BASE",
            prioridad=10,
            acumulable=False,
            fecha_inicio=hoy - timedelta(days=1),
            fecha_fin=hoy + timedelta(days=15),
        )
        AsignacionImpuesto.objects.create(
            regla=regla,
            ambito="EMPLEADO",
            empleado=empleado,
            prioridad_local=10,
        )
        total = calcular_impuestos_y_snapshots(
            origen="EMPLEADO_CONCEPTO",
            origen_id=1001,
            tipo_sujeto="EMPLEADO",
            subtotal=Decimal("0.00"),
            empleado=empleado,
        )
        self.assertEqual(total, Decimal("0.00"))
        empleado.salario_base = Decimal("1000.00")
        empleado.save(update_fields=["salario_base"])
        total = calcular_impuestos_y_snapshots(
            origen="EMPLEADO_CONCEPTO",
            origen_id=1002,
            tipo_sujeto="EMPLEADO",
            subtotal=Decimal("0.00"),
            empleado=empleado,
        )
        self.assertEqual(total, Decimal("100.00"))
        self.assertTrue(
            SnapshotImpuestoTransaccional.objects.filter(origen="EMPLEADO_CONCEPTO", origen_id=1002).exists()
        )
