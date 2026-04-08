from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Define roles para el sistema empresarial ERP.
    """
    
    class Rol(models.TextChoices):
        CLIENTE = 'CLIENTE', 'Cliente'
        SOCIO = 'SOCIO', 'Socio'
        INTERNO = 'INTERNO', 'Interno'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
    
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        help_text="Rol del usuario en el sistema"
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Número de teléfono del usuario"
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        help_text="Dirección física del usuario"
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de registro en el sistema"
    )
    
    activo_comercialmente = models.BooleanField(
        default=True,
        help_text="Indica si el usuario está activo para operaciones comerciales"
    )
    
    class Meta:
        managed = True
        db_table = "tbl_usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"
    
    def es_cliente(self):
        return self.rol == self.Rol.CLIENTE
    
    def es_socio(self):
        return self.rol == self.Rol.SOCIO
    
    def es_interno(self):
        return self.rol == self.Rol.INTERNO
    
    def es_administrador(self):
        return self.rol == self.Rol.ADMINISTRADOR
    
    def puede_gestionar_inventario(self):
        """Verifica si el usuario puede gestionar inventario"""
        return self.rol in [self.Rol.INTERNO, self.Rol.ADMINISTRADOR]
    
    def puede_aprobar_pedidos(self):
        """Verifica si el usuario puede aprobar pedidos de socios"""
        return self.rol == self.Rol.ADMINISTRADOR
