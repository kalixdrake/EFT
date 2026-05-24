import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, spacing } from '../utils/theme';

export default function QuantitySelector({ value, max, onChange, disabled }) {
  const atMin = value <= 1;
  const atMax = max != null && value >= max;

  return (
    <View style={styles.container}>
      <Pressable
        style={[styles.button, (atMin || disabled) && styles.buttonDisabled]}
        onPress={() => onChange(value - 1)}
        disabled={atMin || disabled}
      >
        <Text style={styles.buttonText}>−</Text>
      </Pressable>
      <Text style={styles.value}>{value}</Text>
      <Pressable
        style={[styles.button, (atMax || disabled) && styles.buttonDisabled]}
        onPress={() => onChange(value + 1)}
        disabled={atMax || disabled}
      >
        <Text style={styles.buttonText}>+</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  button: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: {
    opacity: 0.4,
  },
  buttonText: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
  },
  value: {
    minWidth: 24,
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '600',
  },
});
