import axios from 'axios';
import { getApiBaseUrl } from './config';
import { getAccessToken, getRefreshToken, saveTokens, clearTokens } from '../utils/storage';

let storeRef = null;
let isRefreshing = false;
let refreshQueue = [];

export function setStoreRef(store) {
  storeRef = store;
}

function processQueue(error, token = null) {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  refreshQueue = [];
}

async function forceLogout() {
  await clearTokens();
  if (storeRef) {
    const { logout } = require('../store/authSlice');
    const { resetCart } = require('../store/cartSlice');
    storeRef.dispatch(logout());
    storeRef.dispatch(resetCart());
  }
}

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

apiClient.interceptors.request.use(async (config) => {
  const token = await getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (!originalRequest || error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

  const refreshUrl = `${getApiBaseUrl()}/api/auth/refresh/`;
    if (originalRequest.url?.includes('/api/auth/refresh/') || originalRequest.url?.includes('/api/auth/login/')) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshQueue.push({
          resolve: (token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(apiClient(originalRequest));
          },
          reject,
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const refreshToken = await getRefreshToken();
      if (!refreshToken) {
        forceLogout();
        return Promise.reject(error);
      }

      const { data } = await axios.post(refreshUrl, { refresh: refreshToken });
      await saveTokens(data.access, data.refresh);
      if (storeRef) {
        const { setTokens } = require('../store/authSlice');
        storeRef.dispatch(setTokens({ accessToken: data.access, refreshToken: data.refresh }));
      }
      processQueue(null, data.access);
      originalRequest.headers.Authorization = `Bearer ${data.access}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      forceLogout();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

export default apiClient;
