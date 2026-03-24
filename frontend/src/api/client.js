import axios from 'axios';

export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = async () => {
  const response = await apiClient.get('/');
  return response.data;
};

export const getMetrics = async () => {
  const response = await apiClient.get('/api/v1/metrics');
  return response.data;
};

export const searchMovies = async (query, limit = 10) => {
  const response = await apiClient.get('/api/v1/movies/search', {
    params: { q: query, limit },
  });
  return response.data;
};

export const getUserInfo = async (userId) => {
  const response = await apiClient.get(`/api/v1/user/${userId}`);
  return response.data;
};

export const getRecommendations = async (data) => {
  const response = await apiClient.post('/api/v1/recommend', data);
  return response.data;
};

export default apiClient;
