from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .usuario_model import Usuario


class Socio(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="socio",
        help_text="Usuario asociado a la entidad de negocio socio",
    )
    porcentaje_anticipo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de anticipo acordado para apartados (0-100%)",
    )
    limite_credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Límite de crédito disponible para el socio",
    )
    saldo_pendiente = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Saldo pendiente de pago",
    )
    descuento_especial = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Descuento especial acordado (0-100%)",
    )
    notas_internas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas internas sobre el socio (solo visible para internos/admins)",
    )
    fecha_acuerdo = models.DateField(
        auto_now_add=True,
        help_text="Fecha del acuerdo comercial",
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el perfil de socio está activo",
    )

    class Meta:
        managed = True
        db_table = "tbl_socios"
        verbose_name = "Socio"
        verbose_name_plural = "Socios"

    def __str__(self):
        return f"Socio: {self.usuario.get_full_name() or self.usuario.username}"

    def credito_disponible(self):
        return self.limite_credito - self.saldo_pendiente

    def puede_comprar(self, monto):
        return self.activo and (self.credito_disponible() >= monto)
