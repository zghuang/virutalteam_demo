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

export const alerts = {
  list: () => api.get('/api/alerts'),
  create: (data: { name: string; keyword: string; frequency?: string }) => api.post('/api/alerts', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/api/alerts/${id}`, data),
  delete: (id: number) => api.delete(`/api/alerts/${id}`),
  events: (params?: { alert_id?: number; limit?: number }) => api.get('/api/alerts/events', { params }),
};

export const reports = {
  list: (params?: { report_type?: string; limit?: number }) => api.get('/api/reports', { params }),
  generate: (data: { title: string; description?: string; report_type?: string }) => api.post('/api/reports/generate', data),
  get: (id: number) => api.get(`/api/reports/${id}`),
};

export const search = {
  keyword: (params: { q: string; category?: string; source?: string; date_from?: string; date_to?: string }) =>
    api.get('/api/search', { params }),
  semantic: (q: string, limit = 20) =>
    api.get('/api/search/semantic', { params: { q, limit } }),
};

export default api;
