import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const auth = {
  login: (username: string, password: string) =>
    api.post('/api/auth/login', { username, password }),
  register: (username: string, password: string) =>
    api.post('/api/auth/register', { username, password }),
  me: () => api.get('/api/auth/me'),
};

export const search = {
  keyword: (params: { q: string; category?: string; source?: string; date_from?: string; date_to?: string }) =>
    api.get('/api/search', { params }),
  semantic: (q: string, limit = 20) =>
    api.get('/api/search/semantic', { params: { q, limit } }),
};

export default api;
