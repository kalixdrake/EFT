from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .usuario_model import Usuario


class PerfilSocio(models.Model):
    """
    Perfil extendido para usuarios con rol SOCIO.
    Almacena información específica de acuerdos comerciales.
    """
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_socio',
        limit_choices_to={'rol': Usuario.Rol.SOCIO},
        help_text="Usuario asociado al perfil de socio"
    )
    
    porcentaje_anticipo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de anticipo acordado para apartados (0-100%)"
    )
    
    limite_credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Límite de crédito disponible para el socio"
    )
    
    saldo_pendiente = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Saldo pendiente de pago"
    )
    
    descuento_especial = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Descuento especial acordado (0-100%)"
    )
    
    notas_internas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas internas sobre el socio (solo visible para internos/admins)"
    )
    
    fecha_acuerdo = models.DateField(
        auto_now_add=True,
        help_text="Fecha del acuerdo comercial"
    )
    
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el perfil de socio está activo"
    )
    
    class Meta:
        managed = True
        db_table = "tbl_perfiles_socio"
        verbose_name = "Perfil de Socio"
        verbose_name_plural = "Perfiles de Socios"
    
    def __str__(self):
        return f"Perfil Socio: {self.usuario.get_full_name() or self.usuario.username}"
    
    def credito_disponible(self):
        """Calcula el crédito disponible restante"""
        return self.limite_credito - self.saldo_pendiente
    
    def puede_comprar(self, monto):
        """Verifica si el socio puede realizar una compra por el monto dado"""
        return self.activo and (self.credito_disponible() >= monto)
