import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add async local auth token from Clerk to all requests
api.interceptors.request.use(
  async (config) => {
    // Clerk seamlessly manages the JWT session client-side
    // We inject it into the authorization header so FastAPI can decode it
    if (window.Clerk && window.Clerk.session) {
      const token = await window.Clerk.session.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

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
    // No auth required for browsing
    const response = await axios.get('/api/opportunities', { params });
    return response.data;
  },

  getById: async (id) => {
    // No auth required for viewing details
    const response = await axios.get(`/api/opportunities/${id}`);
    return response.data;
  },

  getRecommendations: async (limit = 10) => {
    // Requires auth
    const response = await api.get('/recommendations', { params: { limit } });
    return response.data;
  },

  getTrending: async () => {
    const response = await axios.get('/api/opportunities/trending');
    return response.data;
  },

  analyzeFit: async (id) => {
    const response = await api.get(`/opportunities/${id}/analyze-fit`);
    return response.data;
  },

  getIdeas: async (id) => {
    const response = await api.get(`/opportunities/${id}/ideas`);
    return response.data;
  },
};

// Tracking API
export const trackingAPI = {
  saveOpportunity: async (opportunityId) => {
    const response = await api.post('/tracked', { opportunity_id: opportunityId });
    return response.data;
  },

  scrapeOpportunity: async (url) => {
    // First, scrape the opportunity into the DB
    const scrapeResponse = await api.post('/opportunities/scrape', { url });
    const opportunityId = scrapeResponse.data.id;

    // Then, automatically track it for the user
    if (opportunityId) {
      const trackResponse = await api.post('/tracked', { opportunity_id: opportunityId });
      return trackResponse.data;
    }
    return scrapeResponse.data;
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
