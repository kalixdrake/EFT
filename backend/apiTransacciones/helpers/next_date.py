from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def _calculate_next_date(current_date, frequency):
    """
    Returns the next date based on the given frequency.
    Adjust according to your frequency choices.
    """
    if frequency == 'DIARIA':
        return current_date + timedelta(days=1)
    elif frequency == 'SEMANAL':
        return current_date + timedelta(weeks=1)
    elif frequency == 'QUINCENAL':
        return current_date + timedelta(days=15)
    elif frequency == 'MENSUAL':
        return current_date + relativedelta(months=1)
    elif frequency == 'TRIMESTRAL':
        return current_date + relativedelta(months=3)
    elif frequency == 'ANUAL':
        return current_date + relativedelta(years=1)
    else:
        return None  # UNICA or unknown