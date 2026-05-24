import { useCallback, useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { shippingApi } from '../api/services';
import ErrorView from './ErrorView';
import { formatPrice } from '../utils/format';
import { colors, spacing } from '../utils/theme';

export default function ShippingSelector({
  cartItems,
  destination,
  onSelectShipping,
  selectedQuoteId,
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quotes, setQuotes] = useState([]);
  const [meta, setMeta] = useState(null);

  const payload = useMemo(() => {
    if (!cartItems?.length || !destination?.city || !destination?.postalCode) return null;
    return {
      cart_items: cartItems.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
      destination_city: destination.city,
      destination_postal_code: destination.postalCode,
    };
  }, [cartItems, destination]);

  const loadQuotes = useCallback(async () => {
    if (!payload) return;
    setLoading(true);
    setError(null);
    try {
      const data = await shippingApi.quote(payload);
      setQuotes(data.quotes || []);
      setMeta({
        weight: data.weight_kg,
        dimensions: data.dimensions,
        credit: data.shipping_credit_available,
      });
      if (data.quotes?.length) {
        const defaultQuote =
          data.quotes.find((quote) => quote.quote_id === selectedQuoteId) || data.quotes[0];
        onSelectShipping?.(defaultQuote);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cotizar envío');
      setQuotes([]);
      setMeta(null);
    } finally {
      setLoading(false);
    }
  }, [payload, selectedQuoteId, onSelectShipping]);

  useEffect(() => {
    loadQuotes();
  }, [loadQuotes]);

  if (!payload) {
    return (
      <View style={styles.emptyCard}>
        <Text style={styles.emptyText}>Completa tu dirección para cotizar el envío.</Text>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={styles.loadingCard}>
        <ActivityIndicator color={colors.primary} />
        <Text style={styles.loadingText}>Cotizando envío...</Text>
      </View>
    );
  }

  if (error) {
    return <ErrorView message={error} onRetry={loadQuotes} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Opciones de envío</Text>
      {meta ? (
        <Text style={styles.metaText}>
          Crédito disponible: {formatPrice(meta.credit)} · Peso: {meta.weight} kg
        </Text>
      ) : null}
      {quotes.map((quote) => {
        const isSelected = quote.quote_id === selectedQuoteId;
        const isFree = Number(quote.cost_after_credit) === 0;
        return (
          <Pressable
            key={quote.quote_id}
            style={[styles.quoteCard, isSelected && styles.quoteSelected]}
            onPress={() => onSelectShipping?.(quote)}
          >
            <View style={styles.quoteHeader}>
              <Text style={styles.quoteCarrier}>{quote.carrier}</Text>
              <Text style={styles.quoteService}>{quote.service}</Text>
            </View>
            <Text style={styles.quoteDetail}>
              {quote.estimated_days} día(s) · {isFree ? 'Envío gratis' : formatPrice(quote.cost_after_credit)}
            </Text>
            <Text style={styles.quoteCost}>
              Costo base: {formatPrice(quote.cost_cop)}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.lg,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  metaText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  quoteCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  quoteSelected: {
    borderColor: colors.primary,
    backgroundColor: '#EFF6FF',
  },
  quoteHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  quoteCarrier: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.text,
  },
  quoteService: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  quoteDetail: {
    fontSize: 13,
    color: colors.text,
  },
  quoteCost: {
    fontSize: 11,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  loadingCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    alignItems: 'center',
    gap: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.lg,
  },
  loadingText: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  emptyCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.lg,
  },
  emptyText: {
    fontSize: 13,
    color: colors.textSecondary,
  },
});
