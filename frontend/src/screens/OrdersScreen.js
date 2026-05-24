import { useCallback, useEffect } from 'react';
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import ErrorView from '../components/ErrorView';
import LoadingSpinner from '../components/LoadingSpinner';
import { fetchOrders } from '../store/orderSlice';
import { formatDate, formatPrice, getOrderStatusLabel } from '../utils/format';
import { colors, spacing } from '../utils/theme';

export default function OrdersScreen({ navigation }) {
  const dispatch = useDispatch();
  const { orders, loading, error } = useSelector((state) => state.orders);

  const loadOrders = useCallback(() => {
    dispatch(fetchOrders());
  }, [dispatch]);

  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  if (loading && orders.length === 0) {
    return <LoadingSpinner />;
  }

  if (error && orders.length === 0) {
    return <ErrorView message={error} onRetry={loadOrders} />;
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={orders}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadOrders} />}
        ListEmptyComponent={
          <Text style={styles.empty}>Aún no tienes pedidos.</Text>
        }
        renderItem={({ item }) => (
          <Pressable
            style={styles.card}
            onPress={() => navigation.navigate('OrderDetail', { orderId: item.id })}
          >
            <View style={styles.row}>
              <Text style={styles.orderId}>Pedido #{item.id}</Text>
              <Text style={styles.status}>{getOrderStatusLabel(item.status)}</Text>
            </View>
            <Text style={styles.date}>{formatDate(item.created_at)}</Text>
            <View style={styles.row}>
              <Text style={styles.meta}>{item.item_count} artículo(s)</Text>
              <Text style={styles.total}>{formatPrice(item.total)}</Text>
            </View>
            <Text style={styles.city}>{item.shipping_city}</Text>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  list: {
    padding: spacing.md,
    flexGrow: 1,
  },
  empty: {
    textAlign: 'center',
    color: colors.textSecondary,
    marginTop: spacing.xl,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 4,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  orderId: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
  },
  status: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.warning,
    textTransform: 'capitalize',
  },
  date: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  meta: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  total: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.primary,
  },
  city: {
    fontSize: 13,
    color: colors.textSecondary,
  },
});
