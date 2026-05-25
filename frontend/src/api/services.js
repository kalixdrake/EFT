import apiClient from './client';

export const authApi = {
  login: (email, password) =>
    apiClient.post('/api/auth/login/', { email, password }).then((r) => r.data),
  register: (payload) =>
    apiClient.post('/api/auth/register/', payload).then((r) => r.data),
  profile: () => apiClient.get('/api/auth/profile/').then((r) => r.data),
};

export const productsApi = {
  list: (params = {}) =>
    apiClient.get('/api/products/', { params }).then((r) => r.data),
  detail: (id) => apiClient.get(`/api/products/${id}/`).then((r) => r.data),
  categories: () => apiClient.get('/api/products/categories/').then((r) => r.data),
};

export const cartApi = {
  get: () => apiClient.get('/api/cart/').then((r) => r.data),
  add: (productId, quantity = 1) =>
    apiClient.post('/api/cart/add/', { product_id: productId, quantity }).then((r) => r.data),
  update: (itemId, quantity) =>
    apiClient.put(`/api/cart/update/${itemId}/`, { quantity }).then((r) => r.data),
  remove: (itemId) =>
    apiClient.delete(`/api/cart/remove/${itemId}/`).then((r) => r.data),
};

export const locationsApi = {
  departments: () => apiClient.get('/api/locations/departments/').then((r) => r.data),
  municipalities: (departmentId) =>
    apiClient
      .get('/api/locations/municipalities/', { params: { department: departmentId } })
      .then((r) => r.data),
  addresses: () => apiClient.get('/api/locations/addresses/').then((r) => r.data),
  createAddress: (payload) =>
    apiClient.post('/api/locations/addresses/', payload).then((r) => r.data),
  updateAddress: (id, payload) =>
    apiClient.put(`/api/locations/addresses/${id}/`, payload).then((r) => r.data),
  deleteAddress: (id) => apiClient.delete(`/api/locations/addresses/${id}/`).then((r) => r.data),
  setDefaultAddress: (id) =>
    apiClient.put(`/api/locations/addresses/${id}/`, { is_default: true }).then((r) => r.data),
};

export const ordersApi = {
  list: () => apiClient.get('/api/orders/').then((r) => r.data),
  detail: (id) => apiClient.get(`/api/orders/${id}/`).then((r) => r.data),
  create: ({ address_id, shipping_quote_id, payment_method, notes }) =>
    apiClient
      .post('/api/orders/create/', { address_id, shipping_quote_id, payment_method, notes })
      .then((r) => r.data),
  retryPayment: (id) => apiClient.post(`/api/orders/${id}/retry-payment/`).then((r) => r.data),
  tracking: (id) => apiClient.get(`/api/orders/${id}/tracking/`).then((r) => r.data),
};

export const shippingApi = {
  quote: (payload) => apiClient.post('/api/shipping/quote/', payload).then((r) => r.data),
};
