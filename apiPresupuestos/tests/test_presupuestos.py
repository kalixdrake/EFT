from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apiPresupuestos.models.presupuesto_model import TransaccionProgramada
from apiCuentas.models.cuenta_model import Cuenta

class PresupuestoViewSetTest(APITestCase):
    fixtures = [
        "json/init_bancos.json",
        "json/init_cuentas.json",
        "json/init_transacciones.json",
        "json/init_presupuestos.json"
    ]

    def test_descontar_saldo_al_ejecutar_presupuesto(self):
        """Si ejecuto un presupuesto tipo EGRESO manualmente, la cuenta debe descontarse,
        el estado del presupuesto debe pasar a EJECUTADA, y debe haber una trasanccion_aplicada."""
        
        url_ejecutar = reverse("presupuestos-ejecutar", args=[1])
        res = self.client.post(url_ejecutar)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        presupuesto = TransaccionProgramada.objects.get(id=1)
        self.assertEqual(presupuesto.estado, "EJECUTADA")
        self.assertIsNotNone(presupuesto.transaccion_aplicada)

        # Verificar impacto en la cuenta (EGRESO, monto 150)
        # Saldo inicial fixture = 1000. 1000 - 150 = 850
        cuenta = Cuenta.objects.get(id=1)
        self.assertEqual(float(cuenta.saldo), 850.0)

    def test_evitar_ejecutar_presupuesto_ya_ejecutado(self):
        """Un presupuesto ya ejecutado no debería volver a debitar ni ejecutarse."""
        url_ejecutar = reverse("presupuestos-ejecutar", args=[1])
        # Primera ejecución
        self.client.post(url_ejecutar)
        
        # Segunda ejecución
        res2 = self.client.post(url_ejecutar)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ya está ejecutada", res2.data["error"])

    def test_cancelar_presupuesto(self):
        """Razonamiento: Un presupuesto se puede cancelar y no afecta la cuenta."""
        url_cancelar = reverse("presupuestos-cancelar", args=[1])
        res = self.client.post(url_cancelar)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        presupuesto = TransaccionProgramada.objects.get(id=1)
        self.assertEqual(presupuesto.estado, "CANCELADA")

