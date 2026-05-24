import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, spacing } from '../utils/theme';

const OPTIONS = [
  { id: 'bold', label: 'Tarjeta / PSE (Bold)', description: 'Paga en línea' },
  { id: 'cod', label: 'Contraentrega', description: 'Paga al recibir' },
];

export default function PaymentMethodSelector({ selectedMethod, onSelectMethod }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Método de pago</Text>
      {OPTIONS.map((option) => {
        const selected = option.id === selectedMethod;
        return (
          <Pressable
            key={option.id}
            style={[styles.card, selected && styles.cardSelected]}
            onPress={() => onSelectMethod?.(option.id)}
          >
            <View style={styles.row}>
              <View style={[styles.radioOuter, selected && styles.radioOuterSelected]}>
                {selected ? <View style={styles.radioInner} /> : null}
              </View>
              <View style={styles.info}>
                <Text style={styles.label}>{option.label}</Text>
                <Text style={styles.description}>{option.description}</Text>
              </View>
            </View>
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
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  cardSelected: {
    borderColor: colors.primary,
    backgroundColor: '#EFF6FF',
  },
  row: {
    flexDirection: 'row',
    gap: spacing.sm,
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
  info: {
    flex: 1,
  },
  label: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.text,
  },
  description: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2,
  },
});
