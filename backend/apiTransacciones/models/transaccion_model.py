from django.db import models
from apiCuentas.models.cuenta_model import Cuenta
from django.utils.timezone import now
from .categorias_model import Categoria
from apiTransacciones.models.programacion_model import ProgramacionTransaccion


class Transaccion(models.Model):
    monto = models.DecimalField(max_digits=32, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_ejecucion = models.DateTimeField(null=True) #Opcional si es una transaccion futura
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='transacciones')
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='transacciones_origen')
    
    # Nuevo campo para documentos fiscales
    documento = models.FileField(
        upload_to='documentos_fiscales/',
        blank=True,
        null=True,
        help_text="Documento fiscal o recibo relacionado (PDF, imagen, etc.)"
    )

    programacion = models.ForeignKey(ProgramacionTransaccion, on_delete=models.SET_NULL, null=True,
                                     blank=True, related_name="transacciones_generadas")

    def __str__(self):
        return f"{self.descripcion} - {self.monto}"

    class Meta:
        managed = True
        db_table = "tbl_transacciones"
