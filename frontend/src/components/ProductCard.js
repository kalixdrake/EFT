import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { formatPrice } from '../utils/format';
import { resolveMediaUrl } from '../utils/media';
import { colors, spacing } from '../utils/theme';

const THUMB_SIZE = 72;

export default function ProductCard({ product, onPress }) {
  const imageUri = resolveMediaUrl(product.image);
  const outOfStock = product.stock === 0 || product.stock == null;

  return (
    <Pressable style={styles.card} onPress={onPress}>
      <View style={styles.imageContainer}>
        {imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.image} resizeMode="contain" />
        ) : (
          <View style={styles.placeholder}>
            <Text style={styles.placeholderText}>Sin imagen</Text>
          </View>
        )}
      </View>

      <View style={styles.content}>
        <Text style={styles.name} numberOfLines={2}>
          {product.name}
        </Text>
        {product.category_name ? (
          <Text style={styles.category} numberOfLines={1}>
            {product.category_name}
          </Text>
        ) : null}
        <View style={styles.footer}>
          <Text style={styles.price}>{formatPrice(product.price)}</Text>
          {outOfStock ? (
            <Text style={styles.outOfStock}>Agotado</Text>
          ) : product.stock != null ? (
            <Text style={styles.stock}>{product.stock} disp.</Text>
          ) : null}
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    marginHorizontal: spacing.md,
    marginBottom: spacing.sm,
    padding: spacing.sm,
    gap: spacing.sm,
  },
  imageContainer: {
    width: THUMB_SIZE,
    height: THUMB_SIZE,
    borderRadius: 8,
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
  },
  image: {
    width: THUMB_SIZE,
    height: THUMB_SIZE,
  },
  placeholder: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xs,
  },
  placeholderText: {
    color: colors.textSecondary,
    fontSize: 10,
    textAlign: 'center',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    gap: 2,
  },
  name: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    lineHeight: 18,
  },
  category: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 4,
    gap: spacing.sm,
  },
  price: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.primary,
  },
  stock: {
    fontSize: 11,
    color: colors.textSecondary,
  },
  outOfStock: {
    fontSize: 11,
    color: colors.error,
    fontWeight: '600',
  },
});
