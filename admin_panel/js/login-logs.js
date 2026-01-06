/**
 * Login Logs JavaScript
 */

document.addEventListener('DOMContentLoaded', async function() {
    if (!window.adminAuth || !window.adminAuth.getAccessToken()) {
        window.location.href = 'login.html';
        return;
    }
    
    await loadLogs();
});

async function loadLogs() {
    try {
        const response = await window.adminAuth.apiRequest('/logs/login');
        if (response.ok) {
            const data = await response.json();
            renderLogs(data.logs || []);
        } else {
            document.getElementById('logsTableBody').innerHTML = 
                '<tr><td colspan="5" class="text-center">Failed to load logs</td></tr>';
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

function renderLogs(logs) {
    const tbody = document.getElementById('logsTableBody');
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No logs found</td></tr>';
        return;
    }
    
    tbody.innerHTML = logs.map(log => {
        const timestamp = log.timestamp 
            ? new Date(log.timestamp).toLocaleString()
            : 'N/A';
        const statusBadge = log.success 
            ? '<span class="badge badge-success">Success</span>'
            : '<span class="badge badge-danger">Failed</span>';
        
        return `
            <tr>
                <td>${timestamp}</td>
                <td>${log.admin_email || 'N/A'}</td>
                <td>${log.ip_address || 'N/A'}</td>
                <td>${log.device_info || log.user_agent || 'N/A'}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    }).join('');
}

async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        await window.adminAuth.logout();
    }
}

