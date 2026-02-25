import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth API
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    if (response.data.access_token) {
      localStorage.setItem('authToken', response.data.access_token);
      localStorage.setItem('userId', response.data.user_id);
    }
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('authToken', response.data.access_token);
      localStorage.setItem('userId', response.data.user_id);
    }
    return response.data;
  },

  logout: async () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Profile API
export const profileAPI = {
  getProfile: async () => {
    const response = await api.get('/profile');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/profile', profileData);
    return response.data;
  },
};

// Opportunities API
export const opportunitiesAPI = {
  search: async (params = {}) => {
    const response = await api.get('/opportunities', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/opportunities/${id}`);
    return response.data;
  },

  getRecommendations: async (limit = 10) => {
    const response = await api.get('/recommendations', { params: { limit } });
    return response.data;
  },
};

// Tracking API
export const trackingAPI = {
  saveOpportunity: async (opportunityId) => {
    const response = await api.post('/tracked', { opportunity_id: opportunityId });
    return response.data;
  },

  getTracked: async () => {
    const response = await api.get('/tracked');
    return response.data;
  },

  removeTracked: async (opportunityId) => {
    await api.delete(`/tracked/${opportunityId}`);
  },

  addParticipation: async (opportunityId, status, notes = null) => {
    const response = await api.post('/participation', {
      opportunity_id: opportunityId,
      status,
      notes,
    });
    return response.data;
  },

  updateParticipation: async (participationId, status, notes = null) => {
    const response = await api.put(`/participation/${participationId}`, {
      status,
      notes,
    });
    return response.data;
  },

  getParticipationHistory: async () => {
    const response = await api.get('/participation');
    return response.data;
  },
};

export default api;
