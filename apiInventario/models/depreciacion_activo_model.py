from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from .activo_fijo_model import ActivoFijo


class DepreciacionActivo(models.Model):
    class Metodo(models.TextChoices):
        LINEAL = "LINEAL", "Lineal"

    activo = models.ForeignKey(ActivoFijo, on_delete=models.CASCADE, related_name="depreciaciones")
    fecha = models.DateField()
    metodo = models.CharField(max_length=20, choices=Metodo.choices, default=Metodo.LINEAL)
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    valor_en_libros = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "tbl_depreciaciones_activo"
        verbose_name = "Depreciacion de Activo"
        verbose_name_plural = "Depreciaciones de Activo"
        ordering = ["-fecha", "-id"]
        unique_together = [("activo", "fecha")]

    def __str__(self):
        return f"{self.activo.codigo_activo} {self.fecha} {self.monto}"

    @staticmethod
    def valor_en_libros_actual(activo: ActivoFijo):
        ultima = activo.depreciaciones.order_by("-fecha", "-id").first()
        return ultima.valor_en_libros if ultima else activo.valor_compra

    @classmethod
    def registrar_lineal(cls, activo: ActivoFijo, fecha, notas: str = ""):
        if activo.estado == ActivoFijo.EstadoActivo.BAJA:
            return None

        valor_en_libros = cls.valor_en_libros_actual(activo)
        minimo = activo.valor_residual
        if valor_en_libros <= minimo:
            return None

        monto = activo.depreciacion_mensual_estimado()
        maximo_depreciable = valor_en_libros - minimo
        if monto > maximo_depreciable:
            monto = maximo_depreciable

        nuevo_valor = valor_en_libros - monto
        if nuevo_valor < minimo:
            nuevo_valor = minimo
            monto = valor_en_libros - minimo

        if monto <= Decimal("0"):
            return None

        return cls.objects.create(
            activo=activo,
            fecha=fecha,
            metodo=cls.Metodo.LINEAL,
            monto=monto,
            valor_en_libros=nuevo_valor,
            notas=notas or "Depreciacion lineal automatica",
        )

