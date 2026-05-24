import { ActivityIndicator, Pressable, StyleSheet, Text } from 'react-native';
import { colors, spacing } from '../utils/theme';

export default function BoldPaymentButton({ onPress, loading, disabled }) {
  return (
    <Pressable
      style={[styles.button, (loading || disabled) && styles.buttonDisabled]}
      onPress={onPress}
      disabled={loading || disabled}
    >
      {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Pagar con Bold</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
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
