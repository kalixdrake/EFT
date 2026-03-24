from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apiCuentas.models.cuenta_model import Cuenta
from apiTransacciones.models.transaccion_model import Transaccion

class TransaccionViewSetTest(APITestCase):
    fixtures = [
        "json/init_bancos.json",
        "json/init_cuentas.json",
        "json/init_transacciones.json"
    ]

    def test_creacion_transaccion_ingreso_actualiza_saldo(self):
        """Si se crea una transaccion tipo INGRESO, el saldo de la cuenta debe aumentar."""
        cuenta_inicial = Cuenta.objects.get(id=1)
        saldo_inicial = cuenta_inicial.saldo

        url = reverse("transaccion-list")
        data = {
            "monto": 500.00,
            "descripcion": "Abono extra",
            "tipo": 1, 
            "categoria": 1,
            "cuenta": 1
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        cuenta_final = Cuenta.objects.get(id=1)
        # El fixture tiene 1000 de saldo inicial, y el INGRESO suma 500
        self.assertEqual(float(cuenta_final.saldo), float(saldo_inicial) + 500.0)

    def test_creacion_transaccion_egreso_actualiza_saldo(self):
        """Si se crea una transaccion tipo EGRESO, el saldo de la cuenta debe disminuir."""
        cuenta_inicial = Cuenta.objects.get(id=1)
        saldo_inicial = cuenta_inicial.saldo

        url = reverse("transaccion-list")
        data = {
            "monto": 200.00,
            "descripcion": "Cena",
            "tipo": 2, 
            "categoria": 1,
            "cuenta": 1
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        cuenta_final = Cuenta.objects.get(id=1)
        # 1000 - 200 = 800
        self.assertEqual(float(cuenta_final.saldo), float(saldo_inicial) - 200.0)

