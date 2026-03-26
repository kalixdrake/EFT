from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)
    egreso = models.BooleanField()

    def __str__(self):
        return self.nombre