import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { logoutUser } from '../store/authSlice';
import { confirmAction } from '../utils/confirm';
import { colors, spacing } from '../utils/theme';

export default function ProfileScreen() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  const handleLogout = () => {
    confirmAction({
      title: 'Cerrar sesión',
      message: '¿Estás seguro de que deseas salir?',
      confirmText: 'Salir',
      cancelText: 'Cancelar',
      onConfirm: () => {
        dispatch(logoutUser());
      },
    });
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.label}>Nombre</Text>
        <Text style={styles.value}>
          {user?.first_name} {user?.last_name}
        </Text>

        <Text style={styles.label}>Correo</Text>
        <Text style={styles.value}>{user?.email}</Text>

        {user?.role ? (
          <>
            <Text style={styles.label}>Rol</Text>
            <Text style={styles.value}>{user.role}</Text>
          </>
        ) : null}
      </View>

      <Pressable style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Cerrar sesión</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.md,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    gap: spacing.xs,
  },
  label: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  value: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  logoutButton: {
    marginTop: spacing.lg,
    backgroundColor: colors.error,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
  },
  logoutText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
});
