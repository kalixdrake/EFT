import { useCallback, useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import ErrorView from '../components/ErrorView';
import LoadingSpinner from '../components/LoadingSpinner';
import { ordersApi } from '../api/services';
import { fetchOrderDetail } from '../store/orderSlice';
import { formatDate, formatPrice, getOrderStatusLabel } from '../utils/format';
import { colors, spacing } from '../utils/theme';

export default function OrderDetailScreen({ route }) {
  const { orderId } = route.params;
  const dispatch = useDispatch();
  const { currentOrder, loading, error } = useSelector((state) => state.orders);
  const [tracking, setTracking] = useState(null);
  const [trackingError, setTrackingError] = useState(null);

  const loadOrder = useCallback(() => {
    dispatch(fetchOrderDetail(orderId));
  }, [dispatch, orderId]);

  useEffect(() => {
    loadOrder();
  }, [loadOrder]);

  useEffect(() => {
    let isMounted = true;
    setTracking(null);
    setTrackingError(null);
    ordersApi
      .tracking(orderId)
      .then((data) => {
        if (isMounted) setTracking(data);
      })
      .catch((err) => {
        if (isMounted) {
          const message = err.response?.data?.detail;
          setTrackingError(message || null);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [orderId]);

  if (loading && !currentOrder) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorView message={error} onRetry={loadOrder} />;
  }

  const order = currentOrder;
  if (!order) return null;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Pedido {order.order_number}</Text>
        <View style={styles.statusBadge}>
          <Text style={styles.statusText}>{getOrderStatusLabel(order.status)}</Text>
        </View>
      </View>

      <Text style={styles.date}>{formatDate(order.created_at)}</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Envío</Text>
        <Text style={styles.text}>{order.address?.line}</Text>
        <Text style={styles.text}>
          {order.address?.municipality?.name}, {order.address?.municipality?.department?.name}
        </Text>
        {order.shipment?.tracking_number ? (
          <Text style={styles.text}>Tracking: {order.shipment.tracking_number}</Text>
        ) : null}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Productos</Text>
        {order.items?.map((item) => (
          <View key={item.id} style={styles.itemRow}>
            <View style={styles.itemInfo}>
              <Text style={styles.itemName}>{item.product_name}</Text>
              <Text style={styles.itemQty}>x{item.quantity}</Text>
            </View>
            <Text style={styles.itemPrice}>{formatPrice(Number(item.price) * item.quantity)}</Text>
          </View>
        ))}
      </View>

      <View style={styles.totalRow}>
        <Text style={styles.totalLabel}>Total</Text>
        <Text style={styles.totalValue}>{formatPrice(order.total)}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Pago</Text>
        <Text style={styles.text}>Método: {order.payment_method}</Text>
        {order.payment_status ? (
          <Text style={styles.text}>Estado: {order.payment_status}</Text>
        ) : null}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tracking</Text>
        {tracking ? (
          <>
            <Text style={styles.text}>
              {tracking.carrier} · {tracking.current_status}
            </Text>
            {tracking.events?.map((event, index) => (
              <View key={index} style={styles.eventRow}>
                <Text style={styles.eventText}>{event.timestamp || event.created_at}</Text>
                <Text style={styles.eventText}>{event.status || event.description}</Text>
              </View>
            ))}
          </>
        ) : trackingError ? (
          <Text style={styles.text}>{trackingError}</Text>
        ) : (
          <Text style={styles.text}>Sin eventos de tracking por ahora.</Text>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.md,
    paddingBottom: spacing.xl,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.text,
  },
  statusBadge: {
    backgroundColor: '#FEF3C7',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    color: colors.warning,
    fontWeight: '700',
    fontSize: 12,
  },
  date: {
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  section: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: spacing.sm,
    color: colors.text,
  },
  text: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  itemInfo: {
    flex: 1,
    marginRight: spacing.sm,
  },
  itemName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  itemQty: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  itemPrice: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.primary,
  },
  eventRow: {
    marginTop: spacing.xs,
  },
  eventText: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  totalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  totalValue: {
    fontSize: 20,
    fontWeight: '800',
    color: colors.primary,
  },
});
