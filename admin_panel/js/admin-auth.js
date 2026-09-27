/**
 * Admin Authentication JavaScript
 * Handles login, token management, and session handling
 */

const API_BASE_URL = 'http://localhost:8000';

// Token management
function getAccessToken() {
    return localStorage.getItem('admin_access_token');
}

function getRefreshToken() {
    return localStorage.getItem('admin_refresh_token');
}

function setTokens(accessToken, refreshToken) {
    localStorage.setItem('admin_access_token', accessToken);
    localStorage.setItem('admin_refresh_token', refreshToken);
}

function clearTokens() {
    localStorage.removeItem('admin_access_token');
    localStorage.removeItem('admin_refresh_token');
    localStorage.removeItem('admin_data');
}

function getAdminData() {
    const data = localStorage.getItem('admin_data');
    return data ? JSON.parse(data) : null;
}

function setAdminData(admin) {
    localStorage.setItem('admin_data', JSON.stringify(admin));
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = getAccessToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        // Handle token refresh on 401
        if (response.status === 401 && endpoint !== '/auth/login') {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                // Retry original request
                headers['Authorization'] = `Bearer ${getAccessToken()}`;
                return fetch(url, { ...options, headers });
            } else {
                // Redirect to login
                window.location.href = 'login.html';
                return response;
            }
        }
        
        return response;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// Refresh access token
async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        
        if (response.ok) {
            const data = await response.json();
            setTokens(data.access_token, data.refresh_token);
            return true;
        }
    } catch (error) {
        console.error('Token refresh error:', error);
    }
    
    clearTokens();
    return false;
}

// Login form handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const loginButton = document.getElementById('loginButton');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Hide messages
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';
            
            // Show loading
            loginButton.disabled = true;
            loginButton.querySelector('.btn-text').style.display = 'none';
            loginButton.querySelector('.btn-loader').style.display = 'inline';
            
            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Store tokens and admin data
                    setTokens(data.access_token, data.refresh_token);
                    setAdminData(data.admin);
                    
                    // Redirect to dashboard
                    window.location.href = 'dashboard.html';
                } else {
                    // Show error
                    errorMessage.textContent = data.detail || 'Login failed. Please check your credentials.';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                errorMessage.textContent = 'Network error. Please check your connection.';
                errorMessage.style.display = 'block';
            } finally {
                // Reset button
                loginButton.disabled = false;
                loginButton.querySelector('.btn-text').style.display = 'inline';
                loginButton.querySelector('.btn-loader').style.display = 'none';
            }
        });
    }
    
    // Check if already logged in
    if (getAccessToken() && window.location.pathname.includes('login.html')) {
        // Check token validity
        apiRequest('/auth/me')
            .then(response => {
                if (response.ok) {
                    window.location.href = 'dashboard.html';
                }
            })
            .catch(() => {
                clearTokens();
            });
    }
});

// Logout function
async function logout() {
    try {
        await apiRequest('/auth/logout', { method: 'POST' });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        clearTokens();
        window.location.href = 'login.html';
    }
}

// Export for use in other scripts
window.adminAuth = {
    apiRequest,
    getAccessToken,
    getRefreshToken,
    getAdminData,
    logout,
    refreshAccessToken
};

