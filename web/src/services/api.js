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

  uploadResume: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/profile/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
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

  semanticSearch: async (query, limit = 10) => {
    const response = await axios.get('/api/opportunities/search/semantic', {
      params: { q: query, limit }
    });
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

  getScoutAnalysis: async (id) => {
    // Strategic 'Alpha' scout report
    const response = await api.get(`/api/opportunities/${id}/scout`);
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
    const scrapeResponse = await api.post('/opportunities/scrape-url', { url });
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

// Teams API
export const teamsAPI = {
  createTeam: async (opportunityId, teamData) => {
    const response = await api.post(`/teams/opportunity/${opportunityId}`, teamData);
    return response.data;
  },

  getTeamsForOpportunity: async (opportunityId) => {
    // No auth required for viewing teams
    const response = await axios.get(`/api/teams/opportunity/${opportunityId}`);
    return response.data;
  },

  getTeam: async (teamId) => {
    const response = await axios.get(`/api/teams/${teamId}`);
    return response.data;
  },

  requestToJoinTeam: async (teamId, message) => {
    const response = await api.post(`/teams/${teamId}/join`, { message });
    return response.data;
  },

  getTeamRequests: async (teamId) => {
    const response = await api.get(`/teams/${teamId}/requests`);
    return response.data;
  },

  processTeamRequest: async (requestId, action) => {
    const response = await api.put(`/teams/requests/${requestId}/${action}`);
    return response.data;
  },

  recommendMembers: async (teamId) => {
    const response = await api.get(`/teams/${teamId}/recommend-members`);
    return response.data;
  },

  recommendTeamsForMe: async (opportunityId) => {
    const response = await api.get(`/teams/recommended/for-me${opportunityId ? `?opportunity_id=${opportunityId}` : ''}`);
    return response.data;
  },

  getBlueprint: async (teamId) => {
    // 48-hour AI Sprint Roadmap
    const response = await api.get(`/api/teams/${teamId}/blueprint`);
    return response.data;
  },

  getPitch: async (teamId) => {
    // Strategic Pitch Assets
    const response = await api.get(`/api/teams/${teamId}/pitch`);
    return response.data;
  },

  auditSubmission: async (teamId, data) => {
    // AI Judge Submission Audit
    const response = await api.post(`/api/teams/${teamId}/audit`, data);
    return response.data;
  },
};

// Interceptor to add Low-Bandwidth header if enabled
api.interceptors.request.use((config) => {
  const isLiteMode = localStorage.getItem('liteMode') === 'true';
  if (isLiteMode) {
    config.headers['X-Low-Bandwidth'] = 'true';
    config.headers['Accept-Encoding'] = 'gzip'; // Request compression
  }
  return config;
});

export default api;
