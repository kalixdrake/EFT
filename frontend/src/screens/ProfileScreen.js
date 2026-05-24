import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { logoutUser } from '../store/authSlice';
import { deleteAddress, fetchAddresses, setDefaultAddress } from '../store/addressSlice';
import { confirmAction } from '../utils/confirm';
import { colors, spacing } from '../utils/theme';

export default function ProfileScreen({ navigation }) {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { addresses, loading, error } = useSelector((state) => state.address);

  const loadAddresses = useCallback(() => {
    dispatch(fetchAddresses());
  }, [dispatch]);

  useEffect(() => {
    loadAddresses();
  }, [loadAddresses]);

  const handleDeleteAddress = (addressId, event) => {
    event?.stopPropagation?.();
    confirmAction({
      title: 'Eliminar dirección',
      message: '¿Quieres eliminar esta dirección?',
      confirmText: 'Eliminar',
      cancelText: 'Cancelar',
      onConfirm: () => dispatch(deleteAddress(addressId)),
    });
  };

  const handleSetDefault = (addressId, event) => {
    event?.stopPropagation?.();
    dispatch(setDefaultAddress(addressId));
  };

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
      <ScrollView contentContainerStyle={styles.content}>
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

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Mis direcciones</Text>
          <Pressable style={styles.addButton} onPress={() => navigation.navigate('AddressForm')}>
            <Text style={styles.addButtonText}>➕ Agregar dirección</Text>
          </Pressable>
        </View>

        {loading && addresses.length === 0 ? (
          <ActivityIndicator color={colors.primary} />
        ) : null}
        {error && addresses.length === 0 ? (
          <Pressable onPress={loadAddresses}>
            <Text style={styles.errorText}>{String(error)} · Reintentar</Text>
          </Pressable>
        ) : null}

        {!loading && !error && addresses.length === 0 ? (
          <Text style={styles.emptyText}>Aún no tienes direcciones guardadas.</Text>
        ) : null}

        {addresses.map((address) => (
          <Pressable
            key={address.id}
            style={styles.addressCard}
            onPress={() => navigation.navigate('AddressForm', { addressId: address.id })}
          >
            <View style={styles.addressHeader}>
              <Text style={styles.addressTitle}>{address.label || 'Dirección'}</Text>
              {address.is_default ? (
                <View style={styles.defaultBadge}>
                  <Text style={styles.defaultBadgeText}>Predeterminada</Text>
                </View>
              ) : null}
            </View>
            <Text style={styles.addressLine}>{address.line}</Text>
            <Text style={styles.addressMeta}>
              {address.municipality?.name}, {address.municipality?.department?.name}
            </Text>

            <View style={styles.addressActions}>
              {!address.is_default ? (
                <Pressable
                  style={styles.actionButton}
                  onPress={(event) => handleSetDefault(address.id, event)}
                >
                  <Text style={styles.actionButtonText}>Establecer predeterminada</Text>
                </Pressable>
              ) : null}
              <Pressable
                style={[styles.actionButton, styles.deleteButton]}
                onPress={(event) => handleDeleteAddress(address.id, event)}
              >
                <Text style={[styles.actionButtonText, styles.deleteButtonText]}>🗑 Eliminar</Text>
              </Pressable>
            </View>
          </Pressable>
        ))}

        <Pressable style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutText}>Cerrar sesión</Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
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
  sectionHeader: {
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
    gap: spacing.xs,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
  },
  addButton: {
    alignSelf: 'flex-start',
  },
  addButtonText: {
    color: colors.primary,
    fontWeight: '600',
  },
  errorText: {
    color: colors.error,
    marginBottom: spacing.sm,
  },
  emptyText: {
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  addressCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.sm,
    gap: 4,
  },
  addressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  addressTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
  },
  defaultBadge: {
    backgroundColor: '#DCFCE7',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 999,
  },
  defaultBadgeText: {
    fontSize: 12,
    color: colors.success,
    fontWeight: '700',
  },
  addressLine: {
    fontSize: 14,
    color: colors.text,
  },
  addressMeta: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  addressActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  actionButton: {
    borderWidth: 1,
    borderColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: 8,
    borderRadius: 8,
  },
  actionButtonText: {
    color: colors.primary,
    fontWeight: '600',
    fontSize: 12,
  },
  deleteButton: {
    borderColor: colors.error,
  },
  deleteButtonText: {
    color: colors.error,
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
