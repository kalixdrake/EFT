from django.db import models
from apiUbicaciones.models.departamento_model import Departamento

class Municipio(models.Model):
    codigo_dane = models.CharField(max_length=5, unique=True, primary_key=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = "tbl_municipios"

    def __str__(self):
        return f"{self.nombre} - {self.departamento.nombre}"