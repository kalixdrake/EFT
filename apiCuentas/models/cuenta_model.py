from django.db import models
from apiBancos.models.banco_model import Banco

class Cuenta(models.Model):
    '''Modelo para las cuentas bancarias.'''
    banco = models.ForeignKey(Banco, on_delete=models.PROTECT, related_name="cuenta_bancaria")
    saldo = models.DecimalField(decimal_places=2, max_digits=32)
    numero = models.CharField(max_length=50, null=True, blank=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "tbl_cuentas"