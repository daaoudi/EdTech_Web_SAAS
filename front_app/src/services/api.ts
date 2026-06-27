
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  
  if (config.data instanceof URLSearchParams) {
    config.headers['Content-Type'] = 'application/x-www-form-urlencoded';
  }
  
  return config;
});

export default api;