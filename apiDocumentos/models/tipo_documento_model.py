from django.db import models


class TipoDocumento(models.Model):
    class TipoPropietario(models.TextChoices):
        EMPRESA = "EMPRESA", "Empresa"
        EMPLEADO = "EMPLEADO", "Empleado"
        CLIENTE = "CLIENTE", "Cliente"
        SOCIO = "SOCIO", "Socio"
        UNIVERSAL = "UNIVERSAL", "Universal"

    codigo = models.CharField(max_length=40, unique=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    propietario_permitido = models.CharField(
        max_length=20,
        choices=TipoPropietario.choices,
        default=TipoPropietario.UNIVERSAL,
    )
    requiere_vencimiento = models.BooleanField(default=False)
    dias_alerta_vencimiento = models.PositiveIntegerField(default=30)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_tipos_documento"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

