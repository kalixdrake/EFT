from django.db import models

class Banco(models.Model):
    """Modelo de banco"""

    nombre = models.CharField(max_length=50)
    
    class Meta:
        managed = True
        db_table = "tbl_bancos"