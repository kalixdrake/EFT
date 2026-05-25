export function formatPrice(value) {
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return '$0';
  }
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(isoString) {
  if (!isoString) return '';
  return new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(isoString));
}

export function getOrderStatusLabel(status) {
  const labels = {
    pending: 'Pendiente',
    pending_cod: 'Pendiente (contraentrega)',
    confirmed: 'Confirmado',
    shipped: 'Enviado',
    delivered: 'Entregado',
    cancelled: 'Cancelado',
  };
  return labels[status] || status;
}

export function getOrderStatusAppearance(status) {
  const appearance = {
    pending: { color: '#D97706', backgroundColor: '#FEF3C7' },
    pending_cod: { color: '#D97706', backgroundColor: '#FEF3C7' },
    confirmed: { color: '#16A34A', backgroundColor: '#DCFCE7' },
    shipped: { color: '#2563EB', backgroundColor: '#DBEAFE' },
    delivered: { color: '#16A34A', backgroundColor: '#DCFCE7' },
    cancelled: { color: '#DC2626', backgroundColor: '#FEE2E2' },
  };
  return appearance[status] || appearance.pending;
}
