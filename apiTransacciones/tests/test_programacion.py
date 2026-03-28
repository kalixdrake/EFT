from datetime import datetime, timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apiCuentas.models.cuenta_model import Cuenta
from apiTransacciones.models.programacion_model import ProgramacionTransaccion
from apiTransacciones.models.transaccion_model import Transaccion
from apiTransacciones.models.categorias_model import Categoria


class ProgramacionTransaccionViewSetTest(APITestCase):
    fixtures = [
        "json/init_bancos.json",
        "json/init_cuentas.json",
        "json/init_categorias_transacciones.json"
    ]

    def setUp(self):
        # URLs
        self.list_url = reverse('programacion-list')
        self.detail_url = lambda pk: reverse('programacion-detail', args=[pk])
        self.ejecutar_url = lambda pk: reverse('programacion-ejecutar', args=[pk])

        # Accounts from fixtures (id 1 and 2 have balances 100,000 and 1,668,000)
        self.cuenta_origen = Cuenta.objects.get(id=2)
        self.cuenta_destino = Cuenta.objects.get(id=1)

        # Categories (ingreso and egreso)
        self.categoria_egreso = Categoria.objects.get(id=3)   # egreso
        self.categoria_ingreso = Categoria.objects.get(id=8)  # ingreso

        # Common data for programmed transactions
        self.programacion_data = {
            "monto": "50000.00",
            "descripcion": "Programación de prueba",
            "fecha_programada": timezone.now() + timedelta(days=7),  # future date
            "categoria": self.categoria_egreso.id,
            "cuenta": self.cuenta_origen.id,
            "frecuencia": "UNICA",
            "estado": "PENDIENTE",
            "activa": True,
        }

    def create_programacion(self, **kwargs):
        data = self.programacion_data.copy()
        data.update(kwargs)
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return ProgramacionTransaccion.objects.get(id=response.data['id'])

    def test_ejecutar_one_time_success(self):
        """Execute a one-time programmed transaction and verify the real transaction is created."""
        programacion = self.create_programacion(frecuencia='UNICA')
        saldo_inicial = self.cuenta_origen.saldo

        response = self.client.post(self.ejecutar_url(programacion.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extract transaction ID from the new response structure
        transaccion_id = response.data['transaccion']['id']
        self.assertIsNotNone(transaccion_id)

        # Check that a real transaction was created
        transaccion = Transaccion.objects.get(id=transaccion_id)
        self.assertEqual(transaccion.monto, Decimal('50000.00'))
        self.assertEqual(transaccion.descripcion, 'Programación de prueba')
        self.assertEqual(transaccion.categoria, self.categoria_egreso)
        self.assertEqual(transaccion.cuenta, self.cuenta_origen)
        self.assertEqual(transaccion.programacion, programacion)

        # Account balance must be updated (decreased)
        self.cuenta_origen.refresh_from_db()
        self.assertEqual(self.cuenta_origen.saldo, saldo_inicial - Decimal('50000.00'))

        # Programmed transaction must be marked as executed and inactive
        programacion.refresh_from_db()
        self.assertEqual(programacion.estado, 'EJECUTADA')
        self.assertFalse(programacion.activa)

    def test_ejecutar_already_executed(self):
        """Cannot execute a transaction that is already executed."""
        programacion = self.create_programacion()
        # Mark as executed (simulate)
        programacion.estado = 'EJECUTADA'
        programacion.save()

        response = self.client.post(self.ejecutar_url(programacion.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ejecutar_inactive(self):
        """Cannot execute an inactive programmed transaction."""
        programacion = self.create_programacion(activa=False)
        response = self.client.post(self.ejecutar_url(programacion.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ejecutar_cancelled(self):
        """Cannot execute a cancelled transaction."""
        programacion = self.create_programacion(estado='CANCELADA', activa=False)
        response = self.client.post(self.ejecutar_url(programacion.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ejecutar_recurring_with_end_date(self):
        """Execute a recurring transaction that has an end date.
        After execution, the next date should be set and the program should remain pending.
        When the next date exceeds the end date, the program should stop.
        """
        now = timezone.now() + timedelta(days=1)
        # Set up a weekly recurring transaction ending after 3 occurrences
        programacion = self.create_programacion(
            frecuencia='SEMANAL',
            fecha_programada=now,
            fecha_fin_repeticion=now + timedelta(days=14),  # 2 weeks from now, allows 3 executions
        )
        saldo_inicial = self.cuenta_origen.saldo

        # First execution
        response1 = self.client.post(self.ejecutar_url(programacion.id))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        trans1_id = response1.data['transaccion']['id']
        trans1 = Transaccion.objects.get(id=trans1_id)

        # Check first execution
        self.cuenta_origen.refresh_from_db()
        self.assertEqual(self.cuenta_origen.saldo, saldo_inicial - Decimal('50000.00'))

        programacion.refresh_from_db()
        # After first execution, the next date should be set and still pending
        self.assertEqual(programacion.estado, 'PENDIENTE')
        self.assertTrue(programacion.activa)
        self.assertIsNotNone(programacion.fecha_programada)
        self.assertGreater(programacion.fecha_programada, now)

        # Second execution
        response2 = self.client.post(self.ejecutar_url(programacion.id))
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.cuenta_origen.refresh_from_db()
        self.assertEqual(self.cuenta_origen.saldo, saldo_inicial - Decimal('100000.00'))

        programacion.refresh_from_db()
        # Still pending, next date updated again
        self.assertEqual(programacion.estado, 'PENDIENTE')
        self.assertTrue(programacion.activa)

        # Third execution: this should be the last because the next date would exceed end date
        response3 = self.client.post(self.ejecutar_url(programacion.id))
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

        self.cuenta_origen.refresh_from_db()
        self.assertEqual(self.cuenta_origen.saldo, saldo_inicial - Decimal('150000.00'))

        programacion.refresh_from_db()
        # After the last allowed execution, the program should be marked as executed and inactive
        self.assertEqual(programacion.estado, 'EJECUTADA')
        self.assertFalse(programacion.activa)


    def test_ejecutar_with_custom_execution_date(self):
        """Allow passing a custom execution date via request body."""
        programacion = self.create_programacion()
        custom_date = timezone.now() - timedelta(days=1)  # past date
        custom_date_iso = custom_date.isoformat()

        response = self.client.post(self.ejecutar_url(programacion.id),
                                    {'fecha_ejecucion': custom_date_iso},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        transaccion_id = response.data['transaccion']['id']
        transaccion = Transaccion.objects.get(id=transaccion_id)
        # The transaction should have the custom execution date
        # Adjust field name if different (e.g., fecha_ejecucion)
        self.assertEqual(transaccion.fecha_ejecucion.date(), custom_date.date())

    def test_filter_transactions_from_programacion(self):
        """Test that the from_programacion filter works."""
        # Create a programmed transaction and execute it
        programacion = self.create_programacion()
        # First execution
        self.client.post(self.ejecutar_url(programacion.id))

        # Create another normal transaction (not from programacion)
        Transaccion.objects.create(
            monto=Decimal('10000.00'),
            descripcion="Normal transaction",
            categoria=self.categoria_egreso,
            cuenta=self.cuenta_origen,
            fecha_ejecucion=timezone.now()
        )

        # Filter by from_programacion=true
        trans_url = reverse('transaccion-list')
        response = self.client.get(trans_url, {'from_programacion': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        # There should be exactly one transaction (the one from the program)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['descripcion'], 'Programación de prueba')

        # Filter by from_programacion=false (or not provided) should return both
        response2 = self.client.get(trans_url)
        data2 = response2.data['results'] if 'results' in response2.data else response2.data
        self.assertEqual(len(data2), 2)

        # Alternatively, filter by programacion__isnull=false (exact id) maybe
        response3 = self.client.get(trans_url, {'programacion': programacion.id})
        data3 = response3.data['results'] if 'results' in response3.data else response3.data
        self.assertEqual(len(data3), 1)
        self.assertEqual(data3[0]['descripcion'], 'Programación de prueba')

    def test_pendientes_action(self):
        """Test the pendientes endpoint returns only pending and active transactions."""
        # Create a pending active
        prog1 = self.create_programacion(estado='PENDIENTE', activa=True)
        # Create an executed transaction
        prog2 = self.create_programacion(estado='EJECUTADA', activa=False)
        # Create a cancelled transaction
        prog3 = self.create_programacion(estado='CANCELADA', activa=False)

        pendientes_url = reverse('programacion-pendientes')
        response = self.client.get(pendientes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], prog1.id)

    def test_activas_action(self):
        """Test the activas endpoint returns only active transactions."""
        prog1 = self.create_programacion(activa=True)
        prog2 = self.create_programacion(activa=False)
        activas_url = reverse('programacion-activas')
        response = self.client.get(activas_url)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], prog1.id)