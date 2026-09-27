/**
 * Dashboard JavaScript
 * Handles dashboard data loading and agent status toggle
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication
    if (!window.adminAuth || !window.adminAuth.getAccessToken()) {
        window.location.href = 'login.html';
        return;
    }
    
    // Load admin data
    const adminData = window.adminAuth.getAdminData();
    if (adminData) {
        document.getElementById('userName').textContent = adminData.name;
        document.getElementById('userRole').textContent = adminData.role;
        document.getElementById('userAvatar').textContent = adminData.name.charAt(0).toUpperCase();
        
        // Show/hide nav items based on role
        if (adminData.role === 'MASTER_ADMIN') {
            document.getElementById('adminManagementNav').style.display = 'block';
            document.getElementById('systemSettingsNav').style.display = 'block';
        }
    }
    
    // Load dashboard data
    await loadDashboardData();
    
    // Set active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.href.includes('dashboard.html')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
});

async function loadDashboardData() {
    try {
        const response = await window.adminAuth.apiRequest('/system/status');
        if (response.ok) {
            const data = await response.json();
            
            // Update stats
            document.getElementById('totalUsers').textContent = data.total_users || 0;
            document.getElementById('totalAdmins').textContent = data.total_admins || 0;
            document.getElementById('agentActionsToday').textContent = data.agent_actions_today || 0;
            document.getElementById('errorsToday').textContent = data.errors_today || 0;
            
            // Update agent status
            const agentToggle = document.getElementById('agentToggle');
            const agentStatusText = document.getElementById('agentStatusText');
            
            if (data.agent_enabled) {
                agentToggle.classList.add('active');
                agentStatusText.textContent = 'ON';
                agentStatusText.style.color = 'var(--success-color)';
            } else {
                agentToggle.classList.remove('active');
                agentStatusText.textContent = 'OFF';
                agentStatusText.style.color = 'var(--text-secondary)';
            }
        } else {
            console.error('Failed to load dashboard data');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function toggleAgent() {
    const agentToggle = document.getElementById('agentToggle');
    const agentStatusText = document.getElementById('agentStatusText');
    const currentState = agentToggle.classList.contains('active');
    const newState = !currentState;
    
    // Check if user has permission (MASTER_ADMIN only)
    const adminData = window.adminAuth.getAdminData();
    if (adminData.role !== 'MASTER_ADMIN') {
        alert('Only MASTER_ADMIN can toggle agent status');
        return;
    }
    
    try {
        const response = await window.adminAuth.apiRequest('/system/agent-toggle', {
            method: 'POST',
            body: JSON.stringify({ enabled: newState })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.agent_enabled) {
                agentToggle.classList.add('active');
                agentStatusText.textContent = 'ON';
                agentStatusText.style.color = 'var(--success-color)';
            } else {
                agentToggle.classList.remove('active');
                agentStatusText.textContent = 'OFF';
                agentStatusText.style.color = 'var(--text-secondary)';
            }
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to toggle agent status');
        }
    } catch (error) {
        console.error('Error toggling agent:', error);
        alert('Failed to toggle agent status');
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('admin_theme', newTheme);
    
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
}

// Load saved theme
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('admin_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }
});

// Logout function
async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        await window.adminAuth.logout();
    }
}

