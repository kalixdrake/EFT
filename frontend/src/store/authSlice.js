import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authApi } from '../api/services';
import { saveTokens, clearTokens, getAccessToken, getRefreshToken } from '../utils/storage';
import { resetCart } from './cartSlice';

export const initializeAuth = createAsyncThunk('auth/initialize', async (_, { rejectWithValue }) => {
  try {
    const accessToken = await getAccessToken();
    const refreshToken = await getRefreshToken();
    if (!accessToken || !refreshToken) {
      return { user: null, accessToken: null, refreshToken: null };
    }
    const user = await authApi.profile();
    return { user, accessToken, refreshToken };
  } catch (error) {
    await clearTokens();
    return rejectWithValue(error.response?.data?.detail || 'Session expired');
  }
});

export const loginUser = createAsyncThunk('auth/login', async ({ email, password }, { rejectWithValue }) => {
  try {
    const tokens = await authApi.login(email, password);
    await saveTokens(tokens.access, tokens.refresh);
    const user = await authApi.profile();
    return { user, accessToken: tokens.access, refreshToken: tokens.refresh };
  } catch (error) {
    const detail = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0];
    return rejectWithValue(detail || 'Error al iniciar sesión');
  }
});

export const registerUser = createAsyncThunk(
  'auth/register',
  async ({ email, password, first_name, last_name }, { dispatch, rejectWithValue }) => {
    try {
      await authApi.register({ email, password, first_name, last_name });
      return dispatch(loginUser({ email, password })).unwrap();
    } catch (error) {
      const data = error.response?.data;
      const message =
        data?.email?.[0] || data?.password?.[0] || data?.detail || 'Error al registrarse';
      return rejectWithValue(message);
    }
  },
);

export const fetchUserProfile = createAsyncThunk('auth/profile', async (_, { rejectWithValue }) => {
  try {
    return await authApi.profile();
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Error al cargar perfil');
  }
});

export const logoutUser = createAsyncThunk('auth/logout', async (_, { dispatch }) => {
  await clearTokens();
  dispatch(resetCart());
});

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    accessToken: null,
    refreshToken: null,
    loading: false,
    initializing: true,
    error: null,
  },
  reducers: {
    setTokens(state, action) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
    },
    logout(state) {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.error = null;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(initializeAuth.pending, (state) => {
        state.initializing = true;
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.initializing = false;
        state.user = action.payload.user;
        state.accessToken = action.payload.accessToken;
        state.refreshToken = action.payload.refreshToken;
      })
      .addCase(initializeAuth.rejected, (state) => {
        state.initializing = false;
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
      })
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.accessToken = action.payload.accessToken;
        state.refreshToken = action.payload.refreshToken;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(registerUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.accessToken = action.payload.accessToken;
        state.refreshToken = action.payload.refreshToken;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.user = action.payload;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.error = null;
      });
  },
});

export const { setTokens, logout, clearError } = authSlice.actions;
export default authSlice.reducer;
