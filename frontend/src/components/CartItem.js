import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { formatPrice } from '../utils/format';
import { colors, spacing } from '../utils/theme';
import QuantitySelector from './QuantitySelector';

export default function CartItem({ item, onUpdateQuantity, onRemove, loading }) {
  const subtotal = Number(item.product_price) * item.quantity;

  return (
    <View style={styles.container}>
      {item.product_image ? (
        <Image source={{ uri: item.product_image }} style={styles.image} />
      ) : (
        <View style={[styles.image, styles.placeholder]} />
      )}
      <View style={styles.details}>
        <Text style={styles.name} numberOfLines={2}>
          {item.product_name}
        </Text>
        <Text style={styles.price}>{formatPrice(item.product_price)} c/u</Text>
        <View style={styles.row}>
          <QuantitySelector
            value={item.quantity}
            onChange={(qty) => onUpdateQuantity(item.id, qty)}
            disabled={loading}
          />
          <Pressable onPress={() => onRemove(item.id)} disabled={loading}>
            <Text style={styles.remove}>Eliminar</Text>
          </Pressable>
        </View>
        <Text style={styles.subtotal}>Subtotal: {formatPrice(subtotal)}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.sm,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  image: {
    width: 72,
    height: 72,
    borderRadius: 8,
    backgroundColor: colors.background,
  },
  placeholder: {
    backgroundColor: colors.border,
  },
  details: {
    flex: 1,
    gap: 4,
  },
  name: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.text,
  },
  price: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.xs,
  },
  remove: {
    color: colors.error,
    fontSize: 13,
    fontWeight: '600',
  },
  subtotal: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.primary,
    marginTop: 4,
  },
});
