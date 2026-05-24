import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { cartApi } from '../api/services';

function normalizeCart(cart) {
  if (!cart) {
    return { items: [], total: 0 };
  }
  return {
    items: cart.items || [],
    total: Number(cart.total) || 0,
  };
}

export const fetchCart = createAsyncThunk('cart/fetch', async (_, { rejectWithValue }) => {
  try {
    return await cartApi.get();
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Error al cargar el carrito');
  }
});

export const addToCart = createAsyncThunk(
  'cart/add',
  async ({ productId, quantity = 1 }, { rejectWithValue }) => {
    try {
      return await cartApi.add(productId, quantity);
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al agregar al carrito');
    }
  },
);

export const updateCartItem = createAsyncThunk(
  'cart/update',
  async ({ itemId, quantity }, { rejectWithValue }) => {
    try {
      return await cartApi.update(itemId, quantity);
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al actualizar el carrito');
    }
  },
);

export const removeFromCart = createAsyncThunk('cart/remove', async (itemId, { rejectWithValue }) => {
  try {
    return await cartApi.remove(itemId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Error al eliminar del carrito');
  }
});

const cartSlice = createSlice({
  name: 'cart',
  initialState: {
    items: [],
    total: 0,
    loading: false,
    error: null,
  },
  reducers: {
    resetCart(state) {
      state.items = [];
      state.total = 0;
      state.error = null;
    },
    clearCartError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    const pending = (state) => {
      state.loading = true;
      state.error = null;
    };
    const rejected = (state, action) => {
      state.loading = false;
      state.error = action.payload;
    };
    const fulfilled = (state, action) => {
      state.loading = false;
      const normalized = normalizeCart(action.payload);
      state.items = normalized.items;
      state.total = normalized.total;
    };

    builder
      .addCase(fetchCart.pending, pending)
      .addCase(fetchCart.fulfilled, fulfilled)
      .addCase(fetchCart.rejected, rejected)
      .addCase(addToCart.pending, pending)
      .addCase(addToCart.fulfilled, fulfilled)
      .addCase(addToCart.rejected, rejected)
      .addCase(updateCartItem.pending, pending)
      .addCase(updateCartItem.fulfilled, fulfilled)
      .addCase(updateCartItem.rejected, rejected)
      .addCase(removeFromCart.pending, pending)
      .addCase(removeFromCart.fulfilled, fulfilled)
      .addCase(removeFromCart.rejected, rejected);
  },
});

export const { resetCart, clearCartError } = cartSlice.actions;
export default cartSlice.reducer;
