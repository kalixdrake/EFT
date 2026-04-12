from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Identidad técnica del sistema (autenticación/autorización)."""

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
        return f"{self.get_full_name() or self.username}"

    def tipo_entidad_principal(self):
        if hasattr(self, 'empleado'):
            return 'EMPLEADO'
        if hasattr(self, 'socio'):
            return 'SOCIO'
        if hasattr(self, 'cliente'):
            return 'CLIENTE'
        return 'SIN_ENTIDAD'
    
    def es_cliente(self):
        return hasattr(self, 'cliente')
    
    def es_socio(self):
        return hasattr(self, 'socio')
    
    def es_interno(self):
        return hasattr(self, 'empleado')
    
    def es_administrador(self):
        return self.is_superuser or self.groups.filter(name='ADMIN_GENERAL').exists()
    
    def puede_gestionar_inventario(self):
        return self.is_superuser or self.groups.filter(name__in=['ADMIN_GENERAL', 'INVENTARIO', 'LOGISTICA']).exists()
    
    def puede_aprobar_pedidos(self):
        return self.is_superuser or self.groups.filter(name__in=['ADMIN_GENERAL', 'LOGISTICA']).exists()
