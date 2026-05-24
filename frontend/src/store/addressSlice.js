import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { locationsApi } from '../api/services';
import { logoutUser } from './authSlice';

const getDefaultAddressId = (addresses) =>
  addresses.find((address) => address.is_default)?.id || addresses[0]?.id || null;

const applyDefault = (addresses, defaultId) =>
  addresses.map((address) => ({
    ...address,
    is_default: address.id === defaultId,
  }));

export const fetchAddresses = createAsyncThunk(
  'addresses/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      return await locationsApi.addresses();
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al cargar direcciones');
    }
  },
);

export const createAddress = createAsyncThunk(
  'addresses/create',
  async (payload, { rejectWithValue }) => {
    try {
      return await locationsApi.createAddress(payload);
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al crear dirección');
    }
  },
);

export const updateAddress = createAsyncThunk(
  'addresses/update',
  async ({ id, payload }, { rejectWithValue }) => {
    try {
      return await locationsApi.updateAddress(id, payload);
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al actualizar dirección');
    }
  },
);

export const deleteAddress = createAsyncThunk(
  'addresses/delete',
  async (id, { dispatch, rejectWithValue }) => {
    try {
      await locationsApi.deleteAddress(id);
      return id;
    } catch (error) {
      dispatch(fetchAddresses());
      return rejectWithValue(error.response?.data?.detail || 'Error al eliminar dirección');
    }
  },
);

export const setDefaultAddress = createAsyncThunk(
  'addresses/setDefault',
  async (id, { dispatch, rejectWithValue }) => {
    try {
      const updated = await locationsApi.setDefaultAddress(id);
      return updated || { id, is_default: true };
    } catch (error) {
      dispatch(fetchAddresses());
      return rejectWithValue(error.response?.data?.detail || 'Error al marcar como predeterminada');
    }
  },
);

const addressSlice = createSlice({
  name: 'addresses',
  initialState: {
    addresses: [],
    selectedAddressId: null,
    loading: false,
    error: null,
  },
  reducers: {
    setSelectedAddressId(state, action) {
      state.selectedAddressId = action.payload;
    },
    clearSelectedAddress(state) {
      state.selectedAddressId = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAddresses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAddresses.fulfilled, (state, action) => {
        state.loading = false;
        state.addresses = action.payload;
        const selectedExists = state.addresses.some(
          (address) => address.id === state.selectedAddressId,
        );
        if (!selectedExists) {
          state.selectedAddressId = getDefaultAddressId(state.addresses);
        }
      })
      .addCase(fetchAddresses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createAddress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createAddress.fulfilled, (state, action) => {
        state.loading = false;
        const created = action.payload;
        state.addresses = [created, ...state.addresses];
        if (created.is_default) {
          state.addresses = applyDefault(state.addresses, created.id);
        }
        state.selectedAddressId = created.id;
      })
      .addCase(createAddress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(updateAddress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateAddress.fulfilled, (state, action) => {
        state.loading = false;
        const updated = action.payload;
        const index = state.addresses.findIndex((address) => address.id === updated.id);
        if (index >= 0) {
          state.addresses[index] = updated;
        } else {
          state.addresses = [updated, ...state.addresses];
        }
        if (updated.is_default) {
          state.addresses = applyDefault(state.addresses, updated.id);
        }
        state.selectedAddressId = updated.id;
      })
      .addCase(updateAddress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(deleteAddress.pending, (state, action) => {
        state.loading = true;
        state.error = null;
        const removedId = action.meta.arg;
        state.addresses = state.addresses.filter((address) => address.id !== removedId);
        if (state.selectedAddressId === removedId) {
          state.selectedAddressId = getDefaultAddressId(state.addresses);
        }
      })
      .addCase(deleteAddress.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(deleteAddress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(setDefaultAddress.pending, (state, action) => {
        state.loading = true;
        state.error = null;
        const defaultId = action.meta.arg;
        state.addresses = applyDefault(state.addresses, defaultId);
        state.selectedAddressId = defaultId;
      })
      .addCase(setDefaultAddress.fulfilled, (state, action) => {
        state.loading = false;
        const updated = action.payload;
        const index = state.addresses.findIndex((address) => address.id === updated.id);
        if (index >= 0) {
          state.addresses[index] = { ...state.addresses[index], ...updated };
        }
        state.addresses = applyDefault(state.addresses, updated.id);
        state.selectedAddressId = updated.id;
      })
      .addCase(setDefaultAddress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.addresses = [];
        state.selectedAddressId = null;
        state.loading = false;
        state.error = null;
      });
  },
});

export const { setSelectedAddressId, clearSelectedAddress } = addressSlice.actions;
export default addressSlice.reducer;
