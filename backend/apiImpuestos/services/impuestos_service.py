from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from apiUsuarios.models import Empleado

from ..models import AsignacionImpuesto, SnapshotImpuestoTransaccional


def _get_base_amount(base_imponible: str, *, subtotal: Decimal, descuento_pct: Decimal, total_actual: Decimal, salario_base: Decimal | None, monto_explicito: Decimal | None) -> Decimal:
    if base_imponible == "SUBTOTAL":
        return subtotal
    if base_imponible == "SUBTOTAL_MENOS_DESCUENTO":
        return subtotal * (Decimal("1.00") - (descuento_pct / Decimal("100")))
    if base_imponible == "TOTAL_ACTUAL":
        return total_actual
    if base_imponible == "SALARIO_BASE":
        return salario_base or Decimal("0")
    if base_imponible == "MONTO_EXPLICITO":
        return monto_explicito or Decimal("0")
    return subtotal


def _calcular_monto(regla, impuesto, base: Decimal) -> Decimal:
    if impuesto.tipo_calculo == "FIXED":
        return impuesto.monto_fijo
    return (base * impuesto.tasa) / Decimal("100")


def _resolver_asignaciones(tipo_sujeto: str, *, producto=None, empleado: Empleado | None = None, fecha=None):
    hoy = fecha or timezone.now().date()
    filtros_vigencia = Q(regla__fecha_inicio__lte=hoy) & (Q(regla__fecha_fin__isnull=True) | Q(regla__fecha_fin__gte=hoy))
    base_qs = (
        AsignacionImpuesto.objects.select_related("regla", "regla__impuesto")
        .filter(
            activo=True,
            regla__activo=True,
            regla__impuesto__activo=True,
            regla__tipo_sujeto=tipo_sujeto,
        )
        .filter(filtros_vigencia)
    )

    if tipo_sujeto == "PRODUCTO":
        return base_qs.filter(ambito="PRODUCTO", producto=producto).order_by("regla__prioridad", "prioridad_local", "id")
    if tipo_sujeto == "EMPLEADO":
        return base_qs.filter(ambito="EMPLEADO", empleado=empleado).order_by("regla__prioridad", "prioridad_local", "id")
    return base_qs.filter(ambito="EMPRESA").order_by("regla__prioridad", "prioridad_local", "id")


def calcular_impuestos_y_snapshots(
    *,
    origen: str,
    origen_id: int,
    tipo_sujeto: str,
    subtotal: Decimal,
    descuento_pct: Decimal = Decimal("0"),
    producto=None,
    empleado: Empleado | None = None,
    monto_explicito: Decimal | None = None,
):
    asignaciones = _resolver_asignaciones(tipo_sujeto, producto=producto, empleado=empleado)
    total_impuestos = Decimal("0")
    total_actual = subtotal
    snapshots = []

    salario_base = empleado.salario_base if empleado else None

    for asignacion in asignaciones:
        regla = asignacion.regla
        impuesto = regla.impuesto
        base = _get_base_amount(
            regla.base_imponible,
            subtotal=subtotal,
            descuento_pct=descuento_pct,
            total_actual=total_actual,
            salario_base=salario_base,
            monto_explicito=monto_explicito,
        )
        monto = _calcular_monto(regla, impuesto, base)
        if not regla.acumulable:
            total_actual = subtotal
        total_impuestos += monto
        total_actual += monto
        snapshots.append(
            SnapshotImpuestoTransaccional(
                impuesto=impuesto,
                origen=origen,
                origen_id=origen_id,
                nombre_impuesto=impuesto.nombre,
                codigo_impuesto=impuesto.codigo,
                tipo_calculo=impuesto.tipo_calculo,
                base_imponible=base,
                tasa_aplicada=impuesto.tasa,
                monto_fijo_aplicado=impuesto.monto_fijo,
                monto_impuesto=monto,
                prioridad=regla.prioridad,
                acumulable=regla.acumulable,
                fecha_vigencia_inicio=regla.fecha_inicio,
                fecha_vigencia_fin=regla.fecha_fin,
                metadata={"asignacion_id": asignacion.id, "regla_id": regla.id},
            )
        )
    if snapshots:
        SnapshotImpuestoTransaccional.objects.bulk_create(snapshots)
    return total_impuestos

