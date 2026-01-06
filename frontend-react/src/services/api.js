/**
 * API Service
 * Centralized API client with authentication and error handling
 */

import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('kyron_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Network error - no response from server
    if (!error.response) {
      console.error('Network Error:', error.message);
      // Don't redirect on network errors, let components handle it
      return Promise.reject({
        ...error,
        isNetworkError: true,
        message: 'Cannot connect to server. Please check if backend is running.',
      });
    }

    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('kyron_token');
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (email, password) => {
    const response = await api.post(API_ENDPOINTS.AUTH.LOGIN, { email, password });
    if (response.data.token) {
      localStorage.setItem('kyron_token', response.data.token);
    }
    return response.data;
  },
  
  signup: async (email, password, name) => {
    const response = await api.post(API_ENDPOINTS.AUTH.SIGNUP, { email, password, name });
    if (response.data.token) {
      localStorage.setItem('kyron_token', response.data.token);
    }
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('kyron_token');
  },
  
  getToken: () => localStorage.getItem('kyron_token'),
  
  isAuthenticated: () => !!localStorage.getItem('kyron_token'),
};

// Profile API
export const profileAPI = {
  get: async () => {
    const response = await api.get(API_ENDPOINTS.PROFILE.GET);
    return response.data;
  },
  
  update: async (profileData) => {
    const response = await api.put(API_ENDPOINTS.PROFILE.UPDATE, profileData);
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  list: async () => {
    const response = await api.get(API_ENDPOINTS.DOCUMENTS.LIST);
    return response.data;
  },
  
  upload: async (file, description = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }
    
    const response = await api.post(API_ENDPOINTS.DOCUMENTS.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  get: async (id) => {
    const response = await api.get(API_ENDPOINTS.DOCUMENTS.GET(id));
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(API_ENDPOINTS.DOCUMENTS.DELETE(id));
    return response.data;
  },
  
  getText: async (id) => {
    const response = await api.get(API_ENDPOINTS.DOCUMENTS.TEXT(id));
    return response.data;
  },
};

// Automation API
export const automationAPI = {
  trigger: async (url, autoFill = true, serviceData = null) => {
    const payload = {
      url,
      auto_fill: autoFill,
    };
    if (serviceData) {
      payload.service_id = serviceData.serviceId;
      payload.service_config = serviceData.config;
    }
    const response = await api.post(API_ENDPOINTS.AUTOMATION.TRIGGER, payload);
    return response.data;
  },
  
  triggerService: async (serviceId, serviceConfig, autoFill = true) => {
    // Get service URL from catalog
    const catalogResponse = await serviceAPI.getCatalog();
    const service = catalogResponse?.services?.find(s => s.id === serviceId);
    const url = service?.official_url || 'https://example.com';
    
    return automationAPI.trigger(url, autoFill, {
      serviceId,
      config: serviceConfig,
    });
  },
  
  getSessions: async () => {
    const response = await api.get(API_ENDPOINTS.AUTOMATION.SESSIONS);
    return response.data;
  },
  
  getSession: async (id) => {
    const response = await api.get(API_ENDPOINTS.AUTOMATION.SESSION(id).GET);
    return response.data;
  },
  
  getScreenshot: async (id) => {
    const response = await api.get(API_ENDPOINTS.AUTOMATION.SESSION(id).SCREENSHOT);
    return response.data;
  },
  
  fillForm: async (id, fieldMappings) => {
    const response = await api.post(API_ENDPOINTS.AUTOMATION.SESSION(id).FILL, {
      field_mappings: fieldMappings,
    });
    return response.data;
  },
  
  closeSession: async (id) => {
    const response = await api.delete(API_ENDPOINTS.AUTOMATION.SESSION(id).DELETE);
    return response.data;
  },
};

// Service Requests API
export const serviceAPI = {
  getRequests: async () => {
    const response = await api.get(API_ENDPOINTS.SERVICE.REQUESTS);
    return response.data;
  },
  
  createRequest: async (requestData) => {
    const response = await api.post(API_ENDPOINTS.SERVICE.CREATE, requestData);
    return response.data;
  },
  
  getCatalog: async () => {
    const response = await api.get(API_ENDPOINTS.SERVICE.CATALOG);
    return response.data;
  },
};

// Blockchain API
export const blockchainAPI = {
  getInfo: async () => {
    const response = await api.get(API_ENDPOINTS.BLOCKCHAIN.INFO);
    return response.data;
  },
  
  getHistory: async () => {
    const response = await api.get(API_ENDPOINTS.BLOCKCHAIN.HISTORY);
    return response.data;
  },
  
  recordAutomation: async (automationData) => {
    const response = await api.post(API_ENDPOINTS.BLOCKCHAIN.RECORD_AUTOMATION, automationData);
    return response.data;
  },
};

// Voice API
export const voiceAPI = {
  speak: async (text, language = 'en') => {
    const response = await api.post(API_ENDPOINTS.VOICE.SPEAK, { text, language });
    return response.data;
  },
  
  listen: async () => {
    const response = await api.post(API_ENDPOINTS.VOICE.LISTEN);
    return response.data;
  },
  
  getStatus: async () => {
    const response = await api.get(API_ENDPOINTS.VOICE.STATUS);
    return response.data;
  },
};

// Screen Share API
export const screenShareAPI = {
  createSession: async (mode = 'manual') => {
    const response = await api.post(API_ENDPOINTS.SCREEN_SHARE.CREATE_SESSION, { mode });
    return response.data;
  },
  
  getSession: async (id) => {
    const response = await api.get(API_ENDPOINTS.SCREEN_SHARE.SESSION(id).GET);
    return response.data;
  },
  
  setMode: async (id, mode) => {
    const response = await api.put(API_ENDPOINTS.SCREEN_SHARE.SESSION(id).MODE, { mode });
    return response.data;
  },
  
  getScreenshot: async (id) => {
    const response = await api.get(API_ENDPOINTS.SCREEN_SHARE.SESSION(id).SCREENSHOT);
    return response.data;
  },
  
  deleteSession: async (id) => {
    const response = await api.delete(API_ENDPOINTS.SCREEN_SHARE.SESSION(id).DELETE);
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (text, language = 'en') => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/91a57176-fbeb-4748-ba91-9a6dc1d27539',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:274',message:'chatAPI.sendMessage entry',data:{url:API_ENDPOINTS.CHAT.MESSAGE,textLength:text.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    try {
      const response = await api.post(API_ENDPOINTS.CHAT.MESSAGE, { text, language });
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/91a57176-fbeb-4748-ba91-9a6dc1d27539',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:274',message:'chatAPI.sendMessage success',data:{status:response.status,hasData:!!response.data},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      return response.data;
    } catch (error) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/91a57176-fbeb-4748-ba91-9a6dc1d27539',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:274',message:'chatAPI.sendMessage error',data:{error:error.message,hasResponse:!!error.response,status:error.response?.status,isNetworkError:error.isNetworkError},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      throw error;
    }
  },
  
  getHistory: async (limit = 50) => {
    const response = await api.get(`${API_ENDPOINTS.CHAT.HISTORY}?limit=${limit}`);
    return response.data;
  },
  
  clearHistory: async () => {
    const response = await api.delete(API_ENDPOINTS.CHAT.CLEAR);
    return response.data;
  },
};

// Agent API - Combined (Basic operations + Real-world execution)
export const agentAPI = {
  // Basic agent operations
  getState: async () => {
    const response = await api.get(API_ENDPOINTS.AGENT.STATE);
    return response.data;
  },
  
  activate: async () => {
    const response = await api.post(API_ENDPOINTS.AGENT.ACTIVATE);
    return response.data;
  },
  
  deactivate: async () => {
    const response = await api.post(API_ENDPOINTS.AGENT.DEACTIVATE);
    return response.data;
  },
  
  getActivity: async () => {
    const response = await api.get(API_ENDPOINTS.AGENT.ACTIVITY);
    return response.data;
  },
  
  // Real-world execution operations
  start: async (serviceId, serviceConfig = {}) => {
    const response = await api.post(API_ENDPOINTS.AGENT.START, {
      service_id: serviceId,
      service_config: serviceConfig,
      open_in_new_tab: true
    });
    return response.data;
  },
  
  getSession: async (sessionId) => {
    const response = await api.get(API_ENDPOINTS.AGENT.SESSION(sessionId).GET);
    return response.data;
  },
  
  pause: async (sessionId) => {
    const response = await api.post(API_ENDPOINTS.AGENT.SESSION(sessionId).PAUSE);
    return response.data;
  },
  
  resume: async (sessionId) => {
    const response = await api.post(API_ENDPOINTS.AGENT.SESSION(sessionId).RESUME);
    return response.data;
  },
  
  stop: async (sessionId) => {
    const response = await api.post(API_ENDPOINTS.AGENT.SESSION(sessionId).STOP);
    return response.data;
  },
  
  getScreenshot: async (sessionId) => {
    const response = await api.get(API_ENDPOINTS.AGENT.SESSION(sessionId).SCREENSHOT);
    return response.data;
  },
};

export default api;

