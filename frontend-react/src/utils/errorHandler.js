/**
 * Error Handler Utility
 * Provides better error messages for network and API errors
 */

export const handleApiError = (error) => {
  if (!error.response) {
    // Network error - backend not reachable
    return {
      message: 'Cannot connect to server. Please make sure the backend is running on http://127.0.0.1:8000',
      type: 'network',
      details: error.message,
    };
  }

  const status = error.response.status;
  const data = error.response.data;

  switch (status) {
    case 401:
      return {
        message: data.detail || 'Invalid email or password',
        type: 'auth',
      };
    case 403:
      return {
        message: data.detail || 'Access forbidden',
        type: 'permission',
      };
    case 404:
      return {
        message: data.detail || 'Resource not found',
        type: 'not_found',
      };
    case 500:
      return {
        message: data.detail || 'Server error. Please try again later.',
        type: 'server',
      };
    default:
      return {
        message: data.detail || data.message || 'An error occurred',
        type: 'unknown',
      };
  }
};

export const checkBackendHealth = async () => {
  try {
    // Use proxy in dev, direct URL in production
    const healthUrl = import.meta.env.DEV 
      ? '/health'  // Use Vite proxy
      : 'http://127.0.0.1:8000/health';  // Direct URL
    
    const response = await fetch(healthUrl);
    if (response.ok) {
      return { healthy: true };
    }
    return { healthy: false, error: 'Backend returned non-OK status' };
  } catch (error) {
    return {
      healthy: false,
      error: 'Cannot connect to backend. Make sure it\'s running on http://127.0.0.1:8000',
    };
  }
};

