import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { shippingApi } from '../api/services';
import { logoutUser } from './authSlice';

export const fetchShippingQuotes = createAsyncThunk(
  'shipping/fetchQuotes',
  async ({ cartItems, destination }, { rejectWithValue }) => {
    try {
      const payload = {
        cart_items: cartItems.map((item) => ({
          product_id: item.product_id,
          quantity: item.quantity,
        })),
        destination_city: destination.city,
        destination_postal_code: destination.postalCode,
      };
      return await shippingApi.quote(payload);
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al cotizar envío');
    }
  },
);

const shippingSlice = createSlice({
  name: 'shipping',
  initialState: {
    quotes: [],
    selectedQuoteId: null,
    meta: null,
    loading: false,
    error: null,
  },
  reducers: {
    setSelectedQuote(state, action) {
      state.selectedQuoteId = action.payload;
    },
    clearQuotes(state) {
      state.quotes = [];
      state.selectedQuoteId = null;
      state.meta = null;
      state.loading = false;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchShippingQuotes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchShippingQuotes.fulfilled, (state, action) => {
        state.loading = false;
        state.quotes = action.payload.quotes || [];
        state.meta = {
          weight: action.payload.weight_kg,
          dimensions: action.payload.dimensions,
          credit: action.payload.shipping_credit_available,
        };
        const selectedExists = state.quotes.some((quote) => quote.quote_id === state.selectedQuoteId);
        state.selectedQuoteId = selectedExists ? state.selectedQuoteId : state.quotes[0]?.quote_id || null;
      })
      .addCase(fetchShippingQuotes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.quotes = [];
        state.selectedQuoteId = null;
        state.meta = null;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.quotes = [];
        state.selectedQuoteId = null;
        state.meta = null;
        state.loading = false;
        state.error = null;
      });
  },
});

export const { setSelectedQuote, clearQuotes } = shippingSlice.actions;
export default shippingSlice.reducer;
