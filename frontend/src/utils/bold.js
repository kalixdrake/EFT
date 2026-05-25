export const BOLD_LIBRARY_URL = 'https://checkout.bold.co/library/boldPaymentButton.js';

const SUCCESS_STATUSES = new Set(['approved', 'success', 'sale_approved']);
const FAILURE_STATUSES = new Set([
  'cancelled',
  'canceled',
  'declined',
  'failed',
  'failure',
  'rejected',
  'sale_rejected',
]);

export function normalizeBoldStatus(value) {
  const normalized = String(value || '').trim().toLowerCase();
  if (SUCCESS_STATUSES.has(normalized)) {
    return 'success';
  }
  if (FAILURE_STATUSES.has(normalized)) {
    return 'failed';
  }
  return 'pending';
}

export function appendOrderIdToRedirectUrl(redirectUrl, orderId) {
  if (!redirectUrl || !orderId) {
    return redirectUrl;
  }
  const separator = redirectUrl.includes('?') ? '&' : '?';
  if (redirectUrl.includes('orderId=')) {
    return redirectUrl;
  }
  return `${redirectUrl}${separator}orderId=${encodeURIComponent(orderId)}`;
}

export function extractBoldResultFromUrl(rawUrl) {
  if (!rawUrl) {
    return null;
  }

  try {
    const url = new URL(rawUrl);
    const orderReference = url.searchParams.get('bold-order-id');
    const rawStatus = url.searchParams.get('bold-tx-status');
    const orderId = url.searchParams.get('orderId');
    if (!orderReference && !rawStatus && !orderId) {
      return null;
    }
    return {
      orderId: orderId ? Number(orderId) : null,
      orderReference,
      rawStatus,
      status: normalizeBoldStatus(rawStatus),
    };
  } catch (error) {
    return null;
  }
}

export function isBoldRedirectUrl(rawUrl, redirectUrl) {
  const parsed = extractBoldResultFromUrl(rawUrl);
  if (!parsed) {
    return false;
  }
  if (!redirectUrl) {
    return true;
  }

  try {
    const target = new URL(redirectUrl);
    const current = new URL(rawUrl);
    return target.protocol === current.protocol && target.host === current.host && target.pathname === current.pathname;
  } catch (error) {
    return rawUrl.startsWith(redirectUrl.split('?')[0]);
  }
}
