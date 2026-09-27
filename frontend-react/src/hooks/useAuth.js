/**
 * Authentication Hook
 * Manages user authentication state
 */

import { useState, useEffect } from 'react';
import { authAPI } from '../services/api';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Ensure dev/guest token exists
    try {
      if (!localStorage.getItem('kyron_token')) {
        localStorage.setItem('kyron_token', 'dev_kyron_token');
      }
      setIsAuthenticated(true);
      setLoading(false);
    } catch (error) {
      setIsAuthenticated(true);
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

