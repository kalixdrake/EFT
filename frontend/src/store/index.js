import { configureStore } from '@reduxjs/toolkit';
import addressReducer from './addressSlice';
import authReducer from './authSlice';
import cartReducer from './cartSlice';
import orderReducer from './orderSlice';

export const store = configureStore({
  reducer: {
    address: addressReducer,
    auth: authReducer,
    cart: cartReducer,
    orders: orderReducer,
  },
});
