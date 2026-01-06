/**
 * Error Logs JavaScript
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
        const response = await window.adminAuth.apiRequest(`/logs/error?days=${days}`);
        if (response.ok) {
            const data = await response.json();
            renderLogs(data.logs || []);
        } else {
            document.getElementById('logsTableBody').innerHTML = 
                '<tr><td colspan="4" class="text-center">Failed to load logs</td></tr>';
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

function renderLogs(logs) {
    const tbody = document.getElementById('logsTableBody');
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">No logs found</td></tr>';
        return;
    }
    
    tbody.innerHTML = logs.map(log => {
        const timestamp = log.timestamp 
            ? new Date(log.timestamp).toLocaleString()
            : 'N/A';
        const context = log.context ? JSON.stringify(log.context).substring(0, 50) + '...' : 'N/A';
        
        return `
            <tr>
                <td>${timestamp}</td>
                <td><span class="badge badge-danger">${log.error_type || 'N/A'}</span></td>
                <td>${log.message || 'N/A'}</td>
                <td>${context}</td>
            </tr>
        `;
    }).join('');
}

async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        await window.adminAuth.logout();
    }
}

