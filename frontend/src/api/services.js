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

export const ordersApi = {
  list: () => apiClient.get('/api/orders/').then((r) => r.data),
  detail: (id) => apiClient.get(`/api/orders/${id}/`).then((r) => r.data),
  create: (shipping) =>
    apiClient.post('/api/orders/create/', shipping).then((r) => r.data),
};
