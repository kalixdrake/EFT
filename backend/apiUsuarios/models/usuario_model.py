from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        #Externo
        CLIENTE = "Cliente"
        SOCIO = "Socio"
        #Interno
        ADMIN = 'Administrador'
        CONTADOR = 'Contador'
        ABOGADO = 'Abogado'
        EMPLEADO = 'Empleado'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CLIENTE)
    phone = models.CharField(max_length=20)
    
    class Meta:
        db_table = "tbl_usuarios"

    @property
    def is_internal(self):
        return self.role in [self.Roles.ADMIN, self.Roles.CONTADOR, self.Roles.ABOGADO, self.Roles.EMPLEADO]