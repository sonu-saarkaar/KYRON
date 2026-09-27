/**
 * Agent Logs JavaScript
 */

document.addEventListener('DOMContentLoaded', async function() {
    if (!window.adminAuth || !window.adminAuth.getAccessToken()) {
        window.location.href = 'login.html';
        return;
    }
    
    await loadLogs();
});

async function loadLogs() {
    const days = document.getElementById('daysFilter').value;
    
    try {
        const response = await window.adminAuth.apiRequest(`/logs/agent?days=${days}`);
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
        const statusBadge = log.status === 'success' 
            ? '<span class="badge badge-success">Success</span>'
            : log.status === 'error'
            ? '<span class="badge badge-danger">Error</span>'
            : '<span class="badge badge-warning">Pending</span>';
        
        return `
            <tr>
                <td>${timestamp}</td>
                <td>${log.action || 'N/A'}</td>
                <td>${log.form_type || 'N/A'}</td>
                <td>${statusBadge}</td>
                <td>${log.user_id || 'N/A'}</td>
            </tr>
        `;
    }).join('');
}

async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        await window.adminAuth.logout();
    }
}

