/**
 * Authentication Hook
 * Manages user authentication state
 */

import { useState, useEffect } from 'react';
import { authAPI } from '../services/api';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    try {
      const token = authAPI.getToken();
      const authenticated = !!token;
      console.log('[useAuth] Token check:', { hasToken: !!token, authenticated });
      setIsAuthenticated(authenticated);
      setLoading(false);
    } catch (error) {
      console.error('[useAuth] Error checking authentication:', error);
      setIsAuthenticated(false);
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      const data = await authAPI.login(email, password);
      // Ensure token is stored
      if (data.token) {
        localStorage.setItem('kyron_token', data.token);
      }
      // Update authentication state immediately
      setIsAuthenticated(true);
      // Force a small delay to ensure state is updated
      await new Promise(resolve => setTimeout(resolve, 100));
      return { success: true, data };
    } catch (error) {
      setIsAuthenticated(false);
      return {
        success: false,
        error: error.response?.data?.detail || error.message,
      };
    }
  };

  const signup = async (email, password, name) => {
    try {
      const data = await authAPI.signup(email, password, name);
      setIsAuthenticated(true);
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message,
      };
    }
  };

  const logout = () => {
    authAPI.logout();
    setIsAuthenticated(false);
  };

  return {
    isAuthenticated,
    loading,
    login,
    signup,
    logout,
  };
};

