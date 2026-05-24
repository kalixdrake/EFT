import { Alert, Platform } from 'react-native';

export function confirmAction({ title, message, confirmText = 'Confirmar', cancelText = 'Cancelar', onConfirm }) {
  if (Platform.OS === 'web') {
    const accepted = globalThis.confirm(`${title}\n\n${message}`);
    if (accepted) {
      onConfirm();
    }
    return;
  }

  Alert.alert(title, message, [
    { text: cancelText, style: 'cancel' },
    { text: confirmText, style: 'destructive', onPress: onConfirm },
  ]);
}
