// src/api.js
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';  // URL de ton API Django

const api = axios.create({
  baseURL: API_URL,
});

export default api;
