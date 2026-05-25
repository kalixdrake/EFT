import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { ordersApi } from '../api/services';
import { resetCart } from './cartSlice';

function upsertOrder(orders, nextOrder) {
  const nextId = nextOrder?.id;
  if (!nextId) {
    return orders;
  }
  const index = orders.findIndex((order) => order.id === nextId);
  if (index === -1) {
    return [nextOrder, ...orders];
  }
  const cloned = [...orders];
  cloned[index] = { ...cloned[index], ...nextOrder };
  return cloned;
}

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

export const retryOrderPayment = createAsyncThunk(
  'orders/retryPayment',
  async (orderId, { rejectWithValue }) => {
    try {
      return await ordersApi.retryPayment(orderId);
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al reintentar el pago');
    }
  },
);

export const pollOrderStatus = createAsyncThunk(
  'orders/pollStatus',
  async (orderId, { rejectWithValue }) => {
    try {
      return await ordersApi.detail(orderId);
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Error al consultar el pedido');
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
    pollingActive: false,
    pollingError: null,
  },
  reducers: {
    clearCurrentOrder(state) {
      state.currentOrder = null;
    },
    clearOrderError(state) {
      state.error = null;
    },
    updateCurrentOrder(state, action) {
      state.currentOrder = action.payload;
      state.orders = upsertOrder(state.orders, action.payload);
    },
    setPollingActive(state, action) {
      state.pollingActive = action.payload;
    },
    clearPollingError(state) {
      state.pollingError = null;
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
        state.orders = upsertOrder(state.orders, action.payload);
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
        state.orders = upsertOrder(state.orders, action.payload);
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(retryOrderPayment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(retryOrderPayment.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload;
        state.orders = upsertOrder(state.orders, action.payload);
      })
      .addCase(retryOrderPayment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(pollOrderStatus.pending, (state) => {
        state.pollingActive = true;
        state.pollingError = null;
      })
      .addCase(pollOrderStatus.fulfilled, (state, action) => {
        state.pollingActive = false;
        state.currentOrder = action.payload;
        state.orders = upsertOrder(state.orders, action.payload);
      })
      .addCase(pollOrderStatus.rejected, (state, action) => {
        state.pollingActive = false;
        state.pollingError = action.payload;
      });
  },
});

export const {
  clearCurrentOrder,
  clearOrderError,
  updateCurrentOrder,
  setPollingActive,
  clearPollingError,
} = orderSlice.actions;
export default orderSlice.reducer;
