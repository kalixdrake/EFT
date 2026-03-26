from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
import datetime
from decimal import Decimal
from apiCuentas.models.cuenta_model import Cuenta
from apiTransacciones.models.transaccion_model import Transaccion
from apiTransacciones.models.categorias_model import Categoria

class TransaccionViewSetTest(APITestCase):
    fixtures = [
        "json/init_bancos.json",
        "json/init_cuentas.json",
        "json/init_categorias_transacciones.json"
    ]

    def setUp(self):
        self.list_url = reverse('transaccion-list')
        self.transferir_url = reverse('transaccion-transferir')

        # Acorde a las fixtures de cuentas, account 1 tiene saldo 100,000.00
        self.cuenta_origen = Cuenta.objects.get(id=1) 
        # account 2 tiene saldo 1,668,000.00
        self.cuenta_destino = Cuenta.objects.get(id=2) 
        
        # Categorías
        self.categoria_egreso = Categoria.objects.get(id=3) 
        self.categoria_ingreso = Categoria.objects.get(id=8)

        self.transaccion_data_egreso = {
            "monto": "50000.00",
            "descripcion": "Gasto de prueba",
            "categoria": self.categoria_egreso.id,
            "cuenta": self.cuenta_origen.id,
            "fecha_ejecucion": timezone.now().isoformat()
        }

    def test_creacion_transaccion_egreso_exitosa(self):
        saldo_inicial = self.cuenta_origen.saldo
        response = self.client.post(self.list_url, self.transaccion_data_egreso, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Validar que se creó y el saldo se actualizó (restado)
        self.assertEqual(Transaccion.objects.count(), 1)
        self.cuenta_origen.refresh_from_db()
        self.assertEqual(self.cuenta_origen.saldo, saldo_inicial - Decimal('50000.00'))

    def test_creacion_transaccion_ingreso_exitosa(self):
        saldo_inicial = self.cuenta_destino.saldo
        data = {
            "monto": "200000.00",
            "descripcion": "Ingreso de prueba",
            "categoria": self.categoria_ingreso.id,
            "cuenta": self.cuenta_destino.id,
            "fecha_ejecucion": timezone.now().isoformat()
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.cuenta_destino.refresh_from_db()
        self.assertEqual(self.cuenta_destino.saldo, saldo_inicial + Decimal('200000.00'))

    def test_creacion_transaccion_futura_error(self):
        fecha_manana = (timezone.now() + timezone.timedelta(days=1)).isoformat()
        data = self.transaccion_data_egreso.copy()
        data["fecha_ejecucion"] = fecha_manana.isoformat()
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_ejecucion', response.data)
        
    def test_creacion_transaccion_saldo_insuficiente(self):
        data = self.transaccion_data_egreso.copy()
        data["monto"] = "500000.00" # Mayor a los 100,000 que hay en cuenta 1
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('monto', response.data)

    def test_creacion_transaccion_sin_campos_necesarios(self):
        response = self.client.post(self.list_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('monto', response.data)
        self.assertIn('categoria', response.data)
        self.assertIn('cuenta', response.data)
        # Algunos otros campos podrían enviarse en los errrores según el modelo

    def test_transferencia_exitosa(self):
        saldo_inicial_origen = self.cuenta_origen.saldo
        saldo_inicial_destino = self.cuenta_destino.saldo

        data = {
            "cuenta_origen": self.cuenta_origen.id,
            "cuenta_destino": self.cuenta_destino.id,
            "monto": "30000.00",
            "descripcion": "Transferencia de prueba",
            "fecha_ejecucion": timezone.now().isoformat()
        }

        response = self.client.post(self.transferir_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Se deben haber creado dos transacciones (una de ingreso, otra de egreso)
        self.assertEqual(Transaccion.objects.count(), 2)

        # Los saldos deben estar actualizados correctamente
        self.cuenta_origen.refresh_from_db()
        self.cuenta_destino.refresh_from_db()

        self.assertEqual(self.cuenta_origen.saldo, saldo_inicial_origen - Decimal('30000.00'))
        self.assertEqual(self.cuenta_destino.saldo, saldo_inicial_destino + Decimal('30000.00'))

    def test_filtros_transacciones(self):
        # Creamos dos transacciones diferentes para probar el listado
        Transaccion.objects.create(
            monto=Decimal('10000.00'),
            descripcion="Pago de internet",
            categoria=self.categoria_egreso,
            cuenta=self.cuenta_origen,
            fecha_ejecucion=(timezone.now() - timezone.timedelta(days=2)).isoformat()
        )
        Transaccion.objects.create(
            monto=Decimal('50000.00'),
            descripcion="Salario quincenal",
            categoria=self.categoria_ingreso,
            cuenta=self.cuenta_destino,
            fecha_ejecucion=timezone.now().isoformat()
        )

        # Filtro por categoría
        response = self.client.get(self.list_url, {'categoria': self.categoria_egreso.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # if using pagination, results might be under response.data['results'], DRF uses lists if unpaginated
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['descripcion'], "Pago de internet")

        # Filtro por monto min
        response = self.client.get(self.list_url, {'monto_min': '40000.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['descripcion'], "Salario quincenal")

        # Filtro por cuenta
        response = self.client.get(self.list_url, {'cuenta': self.cuenta_origen.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)

    def test_eliminar_transaccion(self):
        t = Transaccion.objects.create(
            monto=Decimal('15000.00'),
            descripcion="Para eliminar",
            categoria=self.categoria_egreso,
            cuenta=self.cuenta_origen,
            fecha_ejecucion=timezone.now().isoformat()
        )
        url_detalle = reverse('transaccion-detail', kwargs={'pk': t.id})
        
        response = self.client.delete(url_detalle)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaccion.objects.count(), 0)

    def test_actualizar_transaccion(self):
        t = Transaccion.objects.create(
            monto=Decimal('15000.00'),
            descripcion="Antes de edit",
            categoria=self.categoria_egreso,
            cuenta=self.cuenta_origen,
            fecha_ejecucion=timezone.now().isoformat()
        )
        url_detalle = reverse('transaccion-detail', kwargs={'pk': t.id})
        
        data = {
            "monto": "15000.00",
            "descripcion": "Despues de edit",
            "categoria": self.categoria_egreso.id,
            "cuenta": self.cuenta_origen.id,
            "fecha_ejecucion": t.fecha_ejecucion.isoformat()
        }
        
        response = self.client.put(url_detalle, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        t.refresh_from_db()
        self.assertEqual(t.descripcion, "Despues de edit")
