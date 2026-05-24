import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Linking,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import BoldPaymentButton from '../components/BoldPaymentButton';
import ErrorView from '../components/ErrorView';
import LoadingSpinner from '../components/LoadingSpinner';
import PaymentMethodSelector from '../components/PaymentMethodSelector';
import ShippingSelector from '../components/ShippingSelector';
import { fetchAddresses, setSelectedAddressId } from '../store/addressSlice';
import { createOrder } from '../store/orderSlice';
import { formatPrice } from '../utils/format';
import { colors, spacing } from '../utils/theme';

function formatAddress(address) {
  const municipality = address.municipality;
  return `${address.line} — ${municipality.name}, ${municipality.department.name}`;
}

export default function CheckoutScreen({ navigation }) {
  const dispatch = useDispatch();
  const { total, items } = useSelector((state) => state.cart);
  const { loading: orderLoading } = useSelector((state) => state.orders);
  const { addresses, selectedAddressId, loading, error } = useSelector((state) => state.address);
  const [selectedQuote, setSelectedQuote] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('bold');

  const loadAddresses = useCallback(() => {
    dispatch(fetchAddresses());
  }, [dispatch]);

  useEffect(() => {
    loadAddresses();
  }, [loadAddresses]);

  useEffect(() => {
    if (!selectedAddressId && addresses.length > 0) {
      const defaultAddress = addresses.find((item) => item.is_default) || addresses[0];
      if (defaultAddress) {
        dispatch(setSelectedAddressId(defaultAddress.id));
      }
    }
  }, [addresses, dispatch, selectedAddressId]);

  const selectedAddress = useMemo(
    () => addresses.find((address) => address.id === selectedAddressId),
    [addresses, selectedAddressId],
  );

  const destination = useMemo(() => {
    if (!selectedAddress) return null;
    return {
      city: selectedAddress.municipality?.name,
      postalCode: selectedAddress.postal_code,
    };
  }, [selectedAddress]);

  const shippingCost = selectedQuote ? Number(selectedQuote.cost_after_credit) : 0;
  const totalWithShipping = total + shippingCost;

  const handleAddAddress = () => {
    navigation.navigate('AddressForm', { source: 'checkout' });
  };

  const handleConfirm = async () => {
    if (!selectedAddressId) {
      Alert.alert('Datos incompletos', 'Selecciona o crea una dirección de envío.');
      return;
    }
    if (!selectedQuote) {
      Alert.alert('Datos incompletos', 'Selecciona una opción de envío.');
      return;
    }

    try {
      const order = await dispatch(
        createOrder({
          address_id: selectedAddressId,
          shipping_quote_id: selectedQuote.quote_id,
          payment_method: paymentMethod,
        }),
      ).unwrap();
      if (paymentMethod === 'bold' && order.bold_data?.checkout_url) {
        await Linking.openURL(order.bold_data.checkout_url);
      }
      navigation.replace('OrderDetail', { orderId: order.id });
    } catch (err) {
      Alert.alert('Error', String(err));
    }
  };

  if (loading && addresses.length === 0) {
    return <LoadingSpinner />;
  }

  if (error && addresses.length === 0) {
    return <ErrorView message={error} onRetry={loadAddresses} />;
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Datos de envío</Text>
        <Text style={styles.subtitle}>
          {items.length} producto(s) · Subtotal: {formatPrice(total)}
        </Text>

        {addresses.length > 0 ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Direcciones guardadas</Text>
            {addresses.map((address) => (
              <Pressable
                key={address.id}
                style={[styles.addressCard, selectedAddressId === address.id && styles.addressSelected]}
                onPress={() => dispatch(setSelectedAddressId(address.id))}
              >
                <View style={styles.addressRow}>
                  <View
                    style={[
                      styles.radioOuter,
                      selectedAddressId === address.id && styles.radioOuterSelected,
                    ]}
                  >
                    {selectedAddressId === address.id ? <View style={styles.radioInner} /> : null}
                  </View>
                  <View style={styles.addressInfo}>
                    <View style={styles.addressHeader}>
                      <Text style={styles.addressText}>{formatAddress(address)}</Text>
                      {address.is_default ? (
                        <View style={styles.defaultBadge}>
                          <Text style={styles.defaultBadgeText}>Predeterminada</Text>
                        </View>
                      ) : null}
                    </View>
                    {address.label ? <Text style={styles.addressLabel}>{address.label}</Text> : null}
                  </View>
                </View>
              </Pressable>
            ))}
          </View>
        ) : (
          <View style={styles.emptyAddress}>
            <Text style={styles.emptyTitle}>No tienes direcciones guardadas.</Text>
            <Pressable style={styles.addAddressButton} onPress={handleAddAddress}>
              <Text style={styles.addAddressText}>➕ Agregar dirección</Text>
            </Pressable>
          </View>
        )}

        <Pressable style={styles.linkButton} onPress={handleAddAddress}>
          <Text style={styles.linkButtonText}>➕ Agregar nueva para este pedido</Text>
        </Pressable>

        {selectedAddress ? (
          <View style={styles.summaryCard}>
            <Text style={styles.sectionTitle}>Dirección seleccionada</Text>
            <Text style={styles.summaryText}>{formatAddress(selectedAddress)}</Text>
            {selectedAddress.label ? (
              <Text style={styles.summaryLabel}>{selectedAddress.label}</Text>
            ) : null}
          </View>
        ) : null}

        <ShippingSelector
          cartItems={items}
          destination={destination}
          selectedQuoteId={selectedQuote?.quote_id}
          onSelectShipping={setSelectedQuote}
        />

        <PaymentMethodSelector
          selectedMethod={paymentMethod}
          onSelectMethod={setPaymentMethod}
        />

        <View style={styles.summaryCard}>
          <Text style={styles.sectionTitle}>Resumen</Text>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryText}>Subtotal</Text>
            <Text style={styles.summaryText}>{formatPrice(total)}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryText}>Envío</Text>
            <Text style={styles.summaryText}>
              {selectedQuote ? formatPrice(shippingCost) : '--'}
            </Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryTotalLabel}>Total</Text>
            <Text style={styles.summaryTotalValue}>
              {selectedQuote ? formatPrice(totalWithShipping) : '--'}
            </Text>
          </View>
        </View>

        {paymentMethod === 'bold' ? (
          <BoldPaymentButton
            loading={orderLoading}
            disabled={!selectedAddressId || !selectedQuote}
            onPress={handleConfirm}
          />
        ) : (
          <Pressable
            style={[styles.button, (orderLoading || !selectedAddressId || !selectedQuote) && styles.buttonDisabled]}
            onPress={handleConfirm}
            disabled={orderLoading || !selectedAddressId || !selectedQuote}
          >
            {orderLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Confirmar pedido</Text>
            )}
          </Pressable>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  addressCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  addressSelected: {
    borderColor: colors.primary,
    backgroundColor: '#EFF6FF',
  },
  section: {
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  addressRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    alignItems: 'flex-start',
  },
  radioOuter: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 2,
  },
  radioOuterSelected: {
    borderColor: colors.primary,
  },
  radioInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
  },
  addressInfo: {
    flex: 1,
  },
  addressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  addressText: {
    fontSize: 14,
    color: colors.text,
    flex: 1,
  },
  addressLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  defaultBadge: {
    backgroundColor: '#DCFCE7',
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: 999,
  },
  defaultBadgeText: {
    fontSize: 10,
    color: colors.success,
    fontWeight: '700',
  },
  linkButton: {
    marginBottom: spacing.md,
  },
  linkButtonText: {
    color: colors.primary,
    fontWeight: '600',
  },
  emptyAddress: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.md,
    alignItems: 'center',
    gap: spacing.sm,
  },
  emptyTitle: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  addAddressButton: {
    borderWidth: 1,
    borderColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 8,
  },
  addAddressText: {
    color: colors.primary,
    fontWeight: '700',
  },
  summaryCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  summaryText: {
    fontSize: 14,
    color: colors.text,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.xs,
  },
  summaryTotalLabel: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.text,
  },
  summaryTotalValue: {
    fontSize: 16,
    fontWeight: '800',
    color: colors.primary,
  },
  summaryLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
});
