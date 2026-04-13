from django.db import models

class Departamento(models.Model):
    codigo_dane = models.CharField(max_length=2,unique=True,primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = "tbl_departamentos"
