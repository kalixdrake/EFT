import { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { locationsApi } from '../api/services';
import { createAddress, fetchAddresses, updateAddress } from '../store/addressSlice';
import { colors, spacing } from '../utils/theme';

const LABEL_OPTIONS = ['Casa', 'Oficina', 'Otro'];

function OptionModal({
  visible,
  title,
  options,
  selectedId,
  loading,
  emptyLabel,
  onClose,
  onSelect,
}) {
  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <Pressable style={StyleSheet.absoluteFill} onPress={onClose} />
        <View style={styles.modalCard}>
          <Text style={styles.modalTitle}>{title}</Text>
          {loading ? (
            <ActivityIndicator color={colors.primary} />
          ) : options.length > 0 ? (
            <ScrollView style={styles.modalList}>
              {options.map((option) => (
                <Pressable
                  key={option.id}
                  style={styles.modalOption}
                  onPress={() => onSelect(option)}
                >
                  <Text
                    style={[
                      styles.modalOptionText,
                      option.id === selectedId && styles.modalOptionTextSelected,
                    ]}
                  >
                    {option.name}
                  </Text>
                </Pressable>
              ))}
            </ScrollView>
          ) : (
            <Text style={styles.modalEmpty}>{emptyLabel}</Text>
          )}
        </View>
      </View>
    </Modal>
  );
}

export default function AddressFormScreen({ navigation, route }) {
  const dispatch = useDispatch();
  const { addresses } = useSelector((state) => state.address);
  const addressId = route.params?.addressId;
  const isEditing = Boolean(addressId);
  const existingAddress = useMemo(
    () => addresses.find((address) => address.id === addressId),
    [addresses, addressId],
  );

  const [line, setLine] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [labelType, setLabelType] = useState('Casa');
  const [customLabel, setCustomLabel] = useState('');
  const [departmentId, setDepartmentId] = useState(null);
  const [municipalityId, setMunicipalityId] = useState(null);
  const [isDefault, setIsDefault] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [municipalities, setMunicipalities] = useState([]);
  const [loadingDepartments, setLoadingDepartments] = useState(true);
  const [loadingMunicipalities, setLoadingMunicipalities] = useState(false);
  const [departmentModalOpen, setDepartmentModalOpen] = useState(false);
  const [municipalityModalOpen, setMunicipalityModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isEditing && !existingAddress) {
      dispatch(fetchAddresses());
    }
  }, [dispatch, existingAddress, isEditing]);

  useEffect(() => {
    let isMounted = true;
    setLoadingDepartments(true);
    locationsApi
      .departments()
      .then((data) => {
        if (isMounted) setDepartments(data);
      })
      .catch(() => {
        if (isMounted) setDepartments([]);
      })
      .finally(() => {
        if (isMounted) setLoadingDepartments(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!departmentId) {
      setMunicipalities([]);
      return;
    }
    let isMounted = true;
    setLoadingMunicipalities(true);
    locationsApi
      .municipalities(departmentId)
      .then((data) => {
        if (isMounted) setMunicipalities(data);
      })
      .catch(() => {
        if (isMounted) setMunicipalities([]);
      })
      .finally(() => {
        if (isMounted) setLoadingMunicipalities(false);
      });
    return () => {
      isMounted = false;
    };
  }, [departmentId]);

  useEffect(() => {
    if (!existingAddress) return;
    setLine(existingAddress.line || '');
    setPostalCode(existingAddress.postal_code || '');
    if (existingAddress.label && LABEL_OPTIONS.includes(existingAddress.label)) {
      setLabelType(existingAddress.label);
      setCustomLabel('');
    } else {
      setLabelType('Otro');
      setCustomLabel(existingAddress.label || '');
    }
    setDepartmentId(existingAddress.municipality?.department?.id || null);
    setMunicipalityId(existingAddress.municipality?.id || null);
    setIsDefault(Boolean(existingAddress.is_default));
  }, [existingAddress]);

  const selectedDepartment = useMemo(
    () => departments.find((department) => department.id === departmentId),
    [departments, departmentId],
  );

  const selectedMunicipality = useMemo(
    () => municipalities.find((municipality) => municipality.id === municipalityId),
    [municipalities, municipalityId],
  );

  const handleSelectDepartment = (department) => {
    setDepartmentId(department.id);
    setMunicipalityId(null);
    setMunicipalities([]);
    setDepartmentModalOpen(false);
  };

  const handleSelectMunicipality = (municipality) => {
    setMunicipalityId(municipality.id);
    setMunicipalityModalOpen(false);
  };

  const labelValue = labelType === 'Otro' ? customLabel.trim() : labelType;

  const handleSave = async () => {
    if (!labelValue || !line.trim() || !postalCode.trim() || !departmentId || !municipalityId) {
      Alert.alert(
        'Datos incompletos',
        'Completa la etiqueta, dirección, código postal, departamento y municipio.',
      );
      return;
    }

    const payload = {
      label: labelValue,
      line: line.trim(),
      postal_code: postalCode.trim(),
      municipality_id: municipalityId,
      is_default: isDefault,
    };

    setSaving(true);
    try {
      if (isEditing) {
        await dispatch(updateAddress({ id: addressId, payload })).unwrap();
      } else {
        await dispatch(createAddress(payload)).unwrap();
      }
      navigation.goBack();
    } catch (error) {
      Alert.alert('Error', String(error));
    } finally {
      setSaving(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>{isEditing ? 'Editar dirección' : 'Nueva dirección'}</Text>
        <Text style={styles.subtitle}>Completa los datos de envío</Text>

        <Text style={styles.fieldLabel}>Etiqueta</Text>
        <View style={styles.chipRow}>
          {LABEL_OPTIONS.map((option) => (
            <Pressable
              key={option}
              style={[styles.chip, labelType === option && styles.chipSelected]}
              onPress={() => setLabelType(option)}
            >
              <Text style={[styles.chipText, labelType === option && styles.chipTextSelected]}>
                {option}
              </Text>
            </Pressable>
          ))}
        </View>
        {labelType === 'Otro' ? (
          <TextInput
            style={styles.input}
            placeholder="Etiqueta personalizada"
            value={customLabel}
            onChangeText={setCustomLabel}
          />
        ) : null}

        <TextInput
          style={styles.input}
          placeholder="Dirección (calle, número, apartamento)"
          value={line}
          onChangeText={setLine}
          autoCapitalize="words"
        />
        <TextInput
          style={styles.input}
          placeholder="Código postal"
          value={postalCode}
          onChangeText={setPostalCode}
          keyboardType="number-pad"
        />

        <Text style={styles.fieldLabel}>Departamento</Text>
        <Pressable style={styles.selectInput} onPress={() => setDepartmentModalOpen(true)}>
          <Text style={selectedDepartment ? styles.selectText : styles.selectPlaceholder}>
            {selectedDepartment?.name || 'Selecciona departamento'}
          </Text>
        </Pressable>

        <Text style={styles.fieldLabel}>Municipio</Text>
        <Pressable
          style={[
            styles.selectInput,
            !departmentId && styles.selectInputDisabled,
          ]}
          onPress={() => departmentId && setMunicipalityModalOpen(true)}
        >
          <Text style={selectedMunicipality ? styles.selectText : styles.selectPlaceholder}>
            {selectedMunicipality?.name || 'Selecciona municipio'}
          </Text>
        </Pressable>

        <View style={styles.switchRow}>
          <Text style={styles.switchLabel}>Establecer como predeterminada</Text>
          <Switch value={isDefault} onValueChange={setIsDefault} />
        </View>

        <Pressable
          style={[styles.button, saving && styles.buttonDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>{isEditing ? 'Guardar cambios' : 'Guardar dirección'}</Text>
          )}
        </Pressable>
      </ScrollView>

      <OptionModal
        visible={departmentModalOpen}
        title="Selecciona departamento"
        options={departments}
        selectedId={departmentId}
        loading={loadingDepartments}
        emptyLabel="No hay departamentos disponibles"
        onClose={() => setDepartmentModalOpen(false)}
        onSelect={handleSelectDepartment}
      />

      <OptionModal
        visible={municipalityModalOpen}
        title="Selecciona municipio"
        options={municipalities}
        selectedId={municipalityId}
        loading={loadingMunicipalities}
        emptyLabel={departmentId ? 'No hay municipios disponibles' : 'Selecciona un departamento primero'}
        onClose={() => setMunicipalityModalOpen(false)}
        onSelect={handleSelectMunicipality}
      />
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  chip: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 999,
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    backgroundColor: colors.surface,
  },
  chipSelected: {
    borderColor: colors.primary,
    backgroundColor: '#EFF6FF',
  },
  chipText: {
    fontSize: 13,
    color: colors.text,
  },
  chipTextSelected: {
    color: colors.primary,
    fontWeight: '700',
  },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: spacing.md,
    paddingVertical: 14,
    fontSize: 16,
    marginBottom: spacing.sm,
  },
  selectInput: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: spacing.md,
    paddingVertical: 14,
    marginBottom: spacing.sm,
  },
  selectInputDisabled: {
    opacity: 0.6,
  },
  selectText: {
    fontSize: 16,
    color: colors.text,
  },
  selectPlaceholder: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginVertical: spacing.sm,
  },
  switchLabel: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.35)',
    justifyContent: 'center',
    padding: spacing.lg,
  },
  modalCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    maxHeight: '70%',
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  modalList: {
    maxHeight: 320,
  },
  modalOption: {
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalOptionText: {
    fontSize: 15,
    color: colors.text,
  },
  modalOptionTextSelected: {
    color: colors.primary,
    fontWeight: '700',
  },
  modalEmpty: {
    fontSize: 14,
    color: colors.textSecondary,
  },
});
