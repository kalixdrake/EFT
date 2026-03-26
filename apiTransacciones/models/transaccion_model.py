from django.db import models
from apiCuentas.models.cuenta_model import Cuenta
from django.utils.timezone import now
from .categorias_model import Categoria

class Transaccion(models.Model):
    monto = models.DecimalField(max_digits=32, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_ejecucion = models.DateTimeField(null=True) #Opcional si es una transaccion futura
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='transacciones')
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='transacciones_origen')

    def __str__(self):
        accion = self.tipo.accion
        return f"{accion} - {self.descripcion} - {self.monto}"

    class Meta:
        managed = True
        db_table = "tbl_transacciones"