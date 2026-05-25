import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { ordersApi } from '../api/services';
import { updateCurrentOrder } from '../store/orderSlice';
import { normalizeBoldStatus } from '../utils/bold';
import { formatPrice, getOrderStatusLabel } from '../utils/format';
import { colors, spacing } from '../utils/theme';

const POLL_INTERVAL_MS = 5000;
const POLL_TIMEOUT_MS = 120_000; // 2 minutes

export default function PaymentResultScreen({ route, navigation }) {
  const { orderId, status: initialStatus } = route.params ?? {};

  // When returning from Bold's hosted checkout (web redirect), Bold appends
  // 'bold-tx-status' to the URL. React Navigation passes it as a route param.
  const boldTxStatus = route.params?.['bold-tx-status'];
  const resolvedStatus = initialStatus || normalizeBoldStatus(boldTxStatus) || undefined;
  const dispatch = useDispatch();
  const currentOrder = useSelector((state) => state.orders.currentOrder);

  const [phase, setPhase] = useState(
    resolvedStatus === 'failed' ? 'cancelled' : 'pending',
  );
  const [timedOut, setTimedOut] = useState(false);
  const [pollingError, setPollingError] = useState(null);

  const intervalRef = useRef(null);
  const timeoutRef = useRef(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    intervalRef.current = null;
    timeoutRef.current = null;
  }, []);

  const poll = useCallback(async () => {
    try {
      const order = await ordersApi.detail(orderId);
      dispatch(updateCurrentOrder(order));
      const s = order.status;
      if (s === 'confirmed' || s === 'shipped' || s === 'delivered') {
        setPhase('confirmed');
        stopPolling();
      } else if (s === 'cancelled') {
        setPhase('cancelled');
        stopPolling();
      }
    } catch (err) {
      setPollingError(err.response?.data?.detail || 'Error al consultar el estado del pago');
    }
  }, [orderId, dispatch, stopPolling]);

  useEffect(() => {
    // If Bold already told us it failed, skip polling
    if (phase === 'cancelled') return;

    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);
    timeoutRef.current = setTimeout(() => {
      stopPolling();
      setTimedOut(true);
    }, POLL_TIMEOUT_MS);

    return () => stopPolling();
  }, [phase, poll, stopPolling]);

  const goToOrder = () => navigation.replace('OrderDetail', { orderId });
  const retryPayment = () => navigation.replace('Checkout');

  // ── Confirmed ─────────────────────────────────────────────────────────────
  if (phase === 'confirmed') {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.card}>
          <Text style={styles.emoji}>✅</Text>
          <Text style={styles.cardTitle}>¡Pago confirmado!</Text>
          <Text style={styles.cardSubtitle}>
            Tu pedido ha sido procesado correctamente. Pronto recibirás los detalles de envío.
          </Text>
          {currentOrder ? (
            <View style={styles.summary}>
              <Text style={styles.summaryTitle}>Pedido {currentOrder.order_number}</Text>
              <Text style={styles.summaryStatus}>{getOrderStatusLabel(currentOrder.status)}</Text>
              {currentOrder.total ? (
                <Text style={styles.summaryTotal}>Total: {formatPrice(currentOrder.total)}</Text>
              ) : null}
            </View>
          ) : null}
          <Pressable style={[styles.btn, styles.btnPrimary]} onPress={goToOrder}>
            <Text style={styles.btnPrimaryText}>Ver pedido</Text>
          </Pressable>
        </View>
      </ScrollView>
    );
  }

  // ── Cancelled ─────────────────────────────────────────────────────────────
  if (phase === 'cancelled') {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.card}>
          <Text style={styles.emoji}>❌</Text>
          <Text style={styles.cardTitle}>El pago no pudo procesarse</Text>
          <Text style={styles.cardSubtitle}>
            El pago fue rechazado o cancelado. Puedes intentarlo nuevamente.
          </Text>
          <Pressable style={[styles.btn, styles.btnPrimary]} onPress={retryPayment}>
            <Text style={styles.btnPrimaryText}>Reintentar pago</Text>
          </Pressable>
          <Pressable style={[styles.btn, styles.btnSecondary]} onPress={goToOrder}>
            <Text style={styles.btnSecondaryText}>Ver pedido</Text>
          </Pressable>
        </View>
      </ScrollView>
    );
  }

  // ── Timed out ─────────────────────────────────────────────────────────────
  if (timedOut) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.card}>
          <Text style={styles.emoji}>⏳</Text>
          <Text style={styles.cardTitle}>Verificación en proceso</Text>
          <Text style={styles.cardSubtitle}>
            Tu pago puede estar siendo procesado. Revisa el estado de tu pedido más tarde.
          </Text>
          <Pressable style={[styles.btn, styles.btnPrimary]} onPress={goToOrder}>
            <Text style={styles.btnPrimaryText}>Ver pedido</Text>
          </Pressable>
        </View>
      </ScrollView>
    );
  }

  // ── Pending / polling ─────────────────────────────────────────────────────
  return (
    <View style={[styles.container, styles.centered]}>
      <ActivityIndicator size="large" color={colors.primary} />
      <Text style={styles.loadingTitle}>Confirmando tu pago…</Text>
      <Text style={styles.loadingSubtitle}>
        Estamos verificando el estado de tu transacción. Esto puede tomar unos segundos.
      </Text>
      {pollingError ? <Text style={styles.errorText}>{pollingError}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  content: {
    padding: spacing.lg,
    flexGrow: 1,
    justifyContent: 'center',
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: spacing.xl,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    gap: spacing.md,
  },
  emoji: {
    fontSize: 48,
  },
  cardTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.text,
    textAlign: 'center',
  },
  cardSubtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
  summary: {
    width: '100%',
    backgroundColor: colors.background,
    borderRadius: 10,
    padding: spacing.md,
    alignItems: 'center',
    gap: spacing.xs,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
  },
  summaryStatus: {
    fontSize: 13,
    color: colors.success,
    fontWeight: '600',
  },
  summaryTotal: {
    fontSize: 14,
    color: colors.text,
  },
  btn: {
    width: '100%',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
  },
  btnPrimary: {
    backgroundColor: colors.primary,
  },
  btnPrimaryText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  btnSecondary: {
    borderWidth: 1,
    borderColor: colors.primary,
  },
  btnSecondaryText: {
    color: colors.primary,
    fontSize: 16,
    fontWeight: '600',
  },
  loadingTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
    marginTop: spacing.lg,
    textAlign: 'center',
  },
  loadingSubtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
    marginTop: spacing.sm,
  },
  errorText: {
    fontSize: 13,
    color: colors.error,
    textAlign: 'center',
    marginTop: spacing.sm,
  },
});
