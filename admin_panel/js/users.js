/**
 * User Management JavaScript
 */

document.addEventListener('DOMContentLoaded', async function() {
    if (!window.adminAuth || !window.adminAuth.getAccessToken()) {
        window.location.href = 'login.html';
        return;
    }
    
    await loadUsers();
});

async function loadUsers() {
    try {
        const response = await window.adminAuth.apiRequest('/users');
        if (response.ok) {
            const data = await response.json();
            renderUsers(data.users || []);
        } else {
            document.getElementById('usersTableBody').innerHTML = 
                '<tr><td colspan="5" class="text-center">Failed to load users</td></tr>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function renderUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No users found</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => {
        const createdDate = user.created_at 
            ? new Date(user.created_at).toLocaleDateString()
            : 'N/A';
        const statusBadge = user.status === 'active' 
            ? '<span class="badge badge-success">Active</span>'
            : '<span class="badge badge-danger">Inactive</span>';
        
        return `
            <tr>
                <td>${user.id || user._id || 'N/A'}</td>
                <td>${user.email || 'N/A'}</td>
                <td>${user.name || 'N/A'}</td>
                <td>${statusBadge}</td>
                <td>${createdDate}</td>
            </tr>
        `;
    }).join('');
}

async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        await window.adminAuth.logout();
    }
}

