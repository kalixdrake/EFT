import { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { productsApi } from '../api/services';
import ErrorView from '../components/ErrorView';
import LoadingSpinner from '../components/LoadingSpinner';
import ProductGallery from '../components/ProductGallery';
import MarkdownContent from '../components/MarkdownContent';
import QuantitySelector from '../components/QuantitySelector';
import { addToCart } from '../store/cartSlice';
import { formatPrice } from '../utils/format';
import { colors, spacing } from '../utils/theme';

function showAlert(title, message, buttons) {
  if (Platform.OS === 'web') {
    if (buttons?.length > 1) {
      const goCart = globalThis.confirm(`${title}\n\n${message}\n\n¿Ir al carrito?`);
      if (goCart) {
        buttons[1]?.onPress?.();
      }
    } else {
      globalThis.alert(`${title}\n\n${message}`);
    }
    return;
  }
  Alert.alert(title, message, buttons);
}

export default function ProductDetailScreen({ route, navigation }) {
  const { productId } = route.params;
  const dispatch = useDispatch();
  const cartLoading = useSelector((state) => state.cart.loading);
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState(1);

  const loadProduct = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await productsApi.detail(productId);
      setProduct(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar el producto');
    } finally {
      setLoading(false);
    }
  }, [productId]);

  useEffect(() => {
    loadProduct();
  }, [loadProduct]);

  const handleAddToCart = async () => {
    try {
      await dispatch(addToCart({ productId, quantity })).unwrap();
      showAlert('Carrito', 'Producto agregado al carrito', [
        { text: 'Seguir comprando', style: 'cancel' },
        { text: 'Ver carrito', onPress: () => navigation.navigate('MainTabs', { screen: 'Cart' }) },
      ]);
    } catch (err) {
      showAlert('Error', String(err));
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorView message={error} onRetry={loadProduct} />;
  if (!product) return null;

  const outOfStock = product.stock === 0 || product.stock == null;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.name}>{product.name}</Text>
      {product.category?.name ? (
        <Text style={styles.category}>{product.category.name}</Text>
      ) : null}

      <View style={styles.heroRow}>
        <ProductGallery key={product.id} product={product} />

        <View style={styles.sidebar}>
          <Text style={styles.price}>{formatPrice(product.price)}</Text>

          {product.stock != null && !outOfStock ? (
            <Text style={styles.stock}>{product.stock} unidades disponibles</Text>
          ) : null}
          {outOfStock ? <Text style={styles.outOfStock}>Producto agotado</Text> : null}

          {!outOfStock && (
            <View style={styles.actions}>
              <Text style={styles.quantityLabel}>Cantidad</Text>
              <QuantitySelector
                value={quantity}
                max={product.stock}
                onChange={setQuantity}
                disabled={cartLoading}
              />
              <Pressable
                style={[styles.button, cartLoading && styles.buttonDisabled]}
                onPress={handleAddToCart}
                disabled={cartLoading}
              >
                {cartLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.buttonText}>Agregar al carrito</Text>
                )}
              </Pressable>
            </View>
          )}
        </View>
      </View>

      {product.description ? (
        <View style={styles.descriptionSection}>
          <Text style={styles.sectionTitle}>Descripción</Text>
          <MarkdownContent content={product.description} horizontalPadding={spacing.md * 4} />
        </View>
      ) : null}
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
    gap: spacing.sm,
  },
  name: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.text,
  },
  category: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  heroRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  sidebar: {
    flex: 1,
    minWidth: 140,
    gap: spacing.sm,
  },
  price: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.primary,
  },
  stock: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  outOfStock: {
    fontSize: 14,
    color: colors.error,
    fontWeight: '600',
  },
  actions: {
    marginTop: spacing.sm,
    gap: spacing.sm,
  },
  quantityLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '700',
  },
  descriptionSection: {
    marginTop: spacing.sm,
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: spacing.sm,
    color: colors.text,
  },
});
