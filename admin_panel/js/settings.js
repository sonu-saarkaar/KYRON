/**
 * System Settings JavaScript
 */

document.addEventListener('DOMContentLoaded', async function() {
    if (!window.adminAuth || !window.adminAuth.getAccessToken()) {
        window.location.href = 'login.html';
        return;
    }
    
    // Check if user is MASTER_ADMIN
    const adminData = window.adminAuth.getAdminData();
    if (adminData.role !== 'MASTER_ADMIN') {
        alert('Access denied. MASTER_ADMIN role required.');
        window.location.href = 'dashboard.html';
        return;
    }
    
    await loadSettings();
});

async function loadSettings() {
    try {
        const response = await window.adminAuth.apiRequest('/system/settings');
        if (response.ok) {
            const data = await response.json();
            renderSettings(data.settings || {});
        } else {
            document.getElementById('settingsContent').innerHTML = 
                '<p class="text-center">Failed to load settings</p>';
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

function renderSettings(settings) {
    const content = document.getElementById('settingsContent');
    
    if (Object.keys(settings).length === 0) {
        content.innerHTML = '<p class="text-center">No settings found</p>';
        return;
    }
    
    let html = '<div style="display: flex; flex-direction: column; gap: 20px;">';
    
    for (const [key, value] of Object.entries(settings)) {
        html += `
            <div class="form-group">
                <label>${key.replace(/_/g, ' ').toUpperCase()}</label>
                <input type="text" id="setting_${key}" value="${value}" 
                       style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid var(--border-color);">
            </div>
        `;
    }
    
    html += `
        <div class="form-actions">
            <button class="btn btn-primary" onclick="saveSettings()">Save Settings</button>
        </div>
    </div>
    `;
    
    content.innerHTML = html;
}

async function saveSettings() {
    const settings = {};
    document.querySelectorAll('[id^="setting_"]').forEach(input => {
        const key = input.id.replace('setting_', '');
        settings[key] = input.value;
    });
    
    try {
        const response = await window.adminAuth.apiRequest('/system/settings', {
            method: 'POST',
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            alert('Settings saved successfully');
            await loadSettings();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to save settings');
        }
    } catch (error) {
        alert('Failed to save settings');
    }
}

async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        await window.adminAuth.logout();
    }
}

