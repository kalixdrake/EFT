import { useMemo, useState } from 'react';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { resolveMediaUrl } from '../utils/media';
import { colors, spacing } from '../utils/theme';

const THUMB_SIZE = 56;
const MAIN_IMAGE_SIZE = 240;

function normalizeImages(product) {
  if (product?.images?.length) {
    return product.images
      .slice()
      .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
      .map((item) => resolveMediaUrl(item.image))
      .filter(Boolean);
  }
  const legacy = resolveMediaUrl(product?.image);
  return legacy ? [legacy] : [];
}

export default function ProductGallery({ product }) {
  const images = useMemo(() => normalizeImages(product), [product]);
  const [selectedIndex, setSelectedIndex] = useState(0);

  const safeIndex = images.length ? Math.min(selectedIndex, images.length - 1) : 0;
  const currentImage = images[safeIndex];

  if (!images.length) {
    return (
      <View style={styles.emptyGallery}>
        <View style={styles.mainImageBox}>
          <Text style={styles.placeholderText}>Sin imagen</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.gallery}>
      {images.length > 1 ? (
        <ScrollView
          style={styles.thumbColumn}
          contentContainerStyle={styles.thumbColumnContent}
          showsVerticalScrollIndicator={false}
        >
          {images.map((uri, index) => {
            const selected = index === safeIndex;
            return (
              <Pressable
                key={`${uri}-${index}`}
                onPress={() => setSelectedIndex(index)}
                style={[styles.thumbButton, selected && styles.thumbButtonSelected]}
              >
                <Image source={{ uri }} style={styles.thumbImage} resizeMode="contain" />
              </Pressable>
            );
          })}
        </ScrollView>
      ) : (
        <View style={styles.thumbColumnPlaceholder} />
      )}

      <View style={styles.mainImageBox}>
        <Image source={{ uri: currentImage }} style={styles.mainImage} resizeMode="contain" />
      </View>
    </View>
  );
}

export { MAIN_IMAGE_SIZE, normalizeImages };

const styles = StyleSheet.create({
  gallery: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.sm,
  },
  thumbColumn: {
    width: THUMB_SIZE + 4,
    maxHeight: MAIN_IMAGE_SIZE,
  },
  thumbColumnContent: {
    gap: spacing.xs,
  },
  thumbColumnPlaceholder: {
    width: 0,
  },
  thumbButton: {
    width: THUMB_SIZE,
    height: THUMB_SIZE,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
  },
  thumbButtonSelected: {
    borderColor: colors.primary,
    borderWidth: 2,
  },
  thumbImage: {
    width: THUMB_SIZE - 6,
    height: THUMB_SIZE - 6,
  },
  mainImageBox: {
    width: MAIN_IMAGE_SIZE,
    height: MAIN_IMAGE_SIZE,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  mainImage: {
    width: MAIN_IMAGE_SIZE,
    height: MAIN_IMAGE_SIZE,
  },
  emptyGallery: {
    flexDirection: 'row',
  },
  placeholderText: {
    color: colors.textSecondary,
    fontSize: 13,
  },
});
