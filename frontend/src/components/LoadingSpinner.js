import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { colors } from '../utils/theme';

export default function LoadingSpinner({ size = 'large' }) {
  return (
    <View style={styles.container}>
      <ActivityIndicator size={size} color={colors.primary} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
});
