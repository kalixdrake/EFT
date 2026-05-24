import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { ordersApi } from '../api/services';
import { resetCart } from './cartSlice';

export const fetchOrders = createAsyncThunk('orders/fetchAll', async (_, { rejectWithValue }) => {
  try {
    return await ordersApi.list();
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Error al cargar pedidos');
  }
});

export const fetchOrderDetail = createAsyncThunk('orders/fetchDetail', async (orderId, { rejectWithValue }) => {
  try {
    return await ordersApi.detail(orderId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Error al cargar el pedido');
  }
});

export const createOrder = createAsyncThunk(
  'orders/create',
  async (shippingData, { dispatch, rejectWithValue }) => {
    try {
      const order = await ordersApi.create(shippingData);
      dispatch(resetCart());
      return order;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al crear el pedido');
    }
  },
);

const orderSlice = createSlice({
  name: 'orders',
  initialState: {
    orders: [],
    currentOrder: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearCurrentOrder(state) {
      state.currentOrder = null;
    },
    clearOrderError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchOrders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.orders = action.payload;
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchOrderDetail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrderDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload;
      })
      .addCase(fetchOrderDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createOrder.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload;
        state.orders = [action.payload, ...state.orders];
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearCurrentOrder, clearOrderError } = orderSlice.actions;
export default orderSlice.reducer;
