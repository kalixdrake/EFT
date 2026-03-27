from datetime import datetime
from django.utils import timezone
from apiTransacciones.helpers.next_date import _calculate_next_date

def get_recurring_occurrences(programacion, start, end):
    """
    Genera todas las fechas de ocurrencia de una programación recurrente
    dentro del rango [start, end].
    """
    occurrences = []
    current = programacion.fecha_programada

    if current > end:
        return occurrences

    # Avanzar hasta la primera ocurrencia dentro del rango
    while current < start:
        next_date = _calculate_next_date(current, programacion.frecuencia)
        if next_date == current:
            break
        current = next_date
        if current > end:
            break

    # Generar todas las ocurrencias
    while current <= end:
        if programacion.fecha_fin_repeticion and current > programacion.fecha_fin_repeticion:
            break
        occurrences.append(current)
        next_date = _calculate_next_date(current, programacion.frecuencia)
        if next_date == current:
            break
        current = next_date

    return occurrences