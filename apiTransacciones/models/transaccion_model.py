from django.db import models
from apiCuentas.models.cuenta_model import Cuenta

class TipoTransaccion(models.Model):
    accion = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.nombre

class CategoriaTransaccion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.nombre

class Transaccion(models.Model):
    monto = models.DecimalField(max_digits=32, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.ForeignKey(TipoTransaccion, on_delete=models.PROTECT, related_name='transacciones')
    categoria = models.ForeignKey(CategoriaTransaccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones')
    cuenta_origen = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='transacciones_origen', null=True, blank=True)
    cuenta_destino = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='transacciones_destino', null=True, blank=True)

    def __str__(self):
        return f"{self.tipo.accion} - {self.descripcion} - {self.monto}"

    class Meta:
        managed = True
        db_table = "tbl_transacciones"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            if self.tipo.id == 3:  # TRANSFERENCIA
                if self.cuenta_origen:
                    self.cuenta_origen.saldo -= self.monto
                    self.cuenta_origen.save()
                if self.cuenta_destino:
                    self.cuenta_destino.saldo += self.monto
                    self.cuenta_destino.save()
            elif self.tipo.id == 4:  # RETIRO
                if self.cuenta_origen:
                    self.cuenta_origen.saldo -= self.monto
                    self.cuenta_origen.save()
                if self.cuenta_destino:
                    self.cuenta_destino.saldo += self.monto
                    self.cuenta_destino.save()
            elif self.tipo.id == 5:  # CONSIGNACION
                if self.cuenta_origen:
                    self.cuenta_origen.saldo -= self.monto
                    self.cuenta_origen.save()
                if self.cuenta_destino:
                    self.cuenta_destino.saldo += self.monto
                    self.cuenta_destino.save()
            else:
                if self.tipo.accion == "INGRESO" and self.cuenta_destino:
                    self.cuenta_destino.saldo += self.monto
                    self.cuenta_destino.save()
                elif self.tipo.accion == "EGRESO" and self.cuenta_origen:
                    self.cuenta_origen.saldo -= self.monto
                    self.cuenta_origen.save()
        super().save(*args, **kwargs)


