/**
 * API Configuration
 * Centralized API configuration for KYRON frontend
 */

// Use proxy in development (via Vite), direct URL in production
// In dev mode, Vite proxy handles /api requests to backend
const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  // In development, use empty string to use Vite proxy
  // In production, use full backend URL
  return import.meta.env.DEV ? '' : 'http://127.0.0.1:8000';
};

export const API_BASE_URL = getApiBaseUrl();
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://127.0.0.1:8000';

export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: `${API_BASE_URL}/api/auth/login`,
    SIGNUP: `${API_BASE_URL}/api/auth/signup`,
    LOGOUT: `${API_BASE_URL}/api/auth/logout`,
  },
  
  // Profile
  PROFILE: {
    GET: `${API_BASE_URL}/api/profile/me`,
    UPDATE: `${API_BASE_URL}/api/profile/update`,
  },
  
  // Documents
  DOCUMENTS: {
    LIST: `${API_BASE_URL}/api/documents`,
    UPLOAD: `${API_BASE_URL}/api/documents/upload`,
    GET: (id) => `${API_BASE_URL}/api/documents/${id}`,
    DELETE: (id) => `${API_BASE_URL}/api/documents/${id}`,
    TEXT: (id) => `${API_BASE_URL}/api/documents/${id}/text`,
  },
  
  // Agent (Basic operations + Real-world execution)
  AGENT: {
    // Basic operations
    STATE: `${API_BASE_URL}/api/agent/state`,
    ACTIVATE: `${API_BASE_URL}/api/agent/activate`,
    DEACTIVATE: `${API_BASE_URL}/api/agent/deactivate`,
    ACTIVITY: `${API_BASE_URL}/api/agent/activity`,
    // Real-world execution
    START: `${API_BASE_URL}/api/agent/start`,
    SESSION: (id) => ({
      GET: `${API_BASE_URL}/api/agent/session/${id}`,
      PAUSE: `${API_BASE_URL}/api/agent/session/${id}/pause`,
      RESUME: `${API_BASE_URL}/api/agent/session/${id}/resume`,
      STOP: `${API_BASE_URL}/api/agent/session/${id}/stop`,
      SCREENSHOT: `${API_BASE_URL}/api/agent/session/${id}/screenshot`,
    }),
  },
  
  // Automation
  AUTOMATION: {
    TRIGGER: `${API_BASE_URL}/api/automation/standalone/trigger`,
    SESSIONS: `${API_BASE_URL}/api/automation/standalone/sessions`,
    SESSION: (id) => ({
      GET: `${API_BASE_URL}/api/automation/standalone/session/${id}`,
      SCREENSHOT: `${API_BASE_URL}/api/automation/standalone/session/${id}/screenshot`,
      FILL: `${API_BASE_URL}/api/automation/standalone/session/${id}/fill`,
      DELETE: `${API_BASE_URL}/api/automation/standalone/session/${id}`,
    }),
  },
  
  // Service Requests
  SERVICE: {
    REQUESTS: `${API_BASE_URL}/api/service/requests`,
    CREATE: `${API_BASE_URL}/api/service/request`,
    CATALOG: `${API_BASE_URL}/api/service/catalog`,
  },
  
  // Blockchain
  BLOCKCHAIN: {
    INFO: `${API_BASE_URL}/api/blockchain/info`,
    HISTORY: `${API_BASE_URL}/api/blockchain/history`,
    RECORD_AUTOMATION: `${API_BASE_URL}/api/blockchain/record/automation`,
  },
  
  // Voice
  VOICE: {
    SPEAK: `${API_BASE_URL}/api/voice/speak`,
    LISTEN: `${API_BASE_URL}/api/voice/listen`,
    STATUS: `${API_BASE_URL}/api/voice/status`,
  },
  
  // Screen Share
  SCREEN_SHARE: {
    CREATE_SESSION: `${API_BASE_URL}/api/screen-share/session/create`,
    SESSION: (id) => ({
      GET: `${API_BASE_URL}/api/screen-share/session/${id}`,
      MODE: `${API_BASE_URL}/api/screen-share/session/${id}/mode`,
      SCREENSHOT: `${API_BASE_URL}/api/screen-share/session/${id}/screenshot`,
      DELETE: `${API_BASE_URL}/api/screen-share/session/${id}`,
    }),
  },
  
  // Chat
  CHAT: {
    MESSAGE: `${API_BASE_URL}/api/chat/message`,
    HISTORY: `${API_BASE_URL}/api/chat/history`,
    CLEAR: `${API_BASE_URL}/api/chat/history`,
  },
};

