/**
 * Admin Management JavaScript
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
    
    await loadAdmins();
    
    // Create admin form handler
    document.getElementById('createAdminForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const adminData = {
            name: document.getElementById('adminName').value,
            email: document.getElementById('adminEmail').value,
            password: document.getElementById('adminPassword').value,
            role: document.getElementById('adminRole').value
        };
        
        try {
            const response = await window.adminAuth.apiRequest('/admins/create', {
                method: 'POST',
                body: JSON.stringify(adminData)
            });
            
            if (response.ok) {
                hideCreateAdminModal();
                await loadAdmins();
                alert('Admin created successfully');
            } else {
                const error = await response.json();
                alert(error.detail || 'Failed to create admin');
            }
        } catch (error) {
            alert('Failed to create admin');
        }
    });
});

async function loadAdmins() {
    try {
        const response = await window.adminAuth.apiRequest('/admins');
        if (response.ok) {
            const admins = await response.json();
            renderAdmins(admins);
        } else {
            document.getElementById('adminsTableBody').innerHTML = 
                '<tr><td colspan="6" class="text-center">Failed to load admins</td></tr>';
        }
    } catch (error) {
        console.error('Error loading admins:', error);
    }
}

function renderAdmins(admins) {
    const tbody = document.getElementById('adminsTableBody');
    
    if (admins.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No admins found</td></tr>';
        return;
    }
    
    tbody.innerHTML = admins.map(admin => {
        const createdDate = new Date(admin.created_at).toLocaleDateString();
        const statusBadge = admin.status === 'active' 
            ? '<span class="badge badge-success">Active</span>'
            : '<span class="badge badge-danger">Blocked</span>';
        
        return `
            <tr>
                <td>${admin.name}</td>
                <td>${admin.email}</td>
                <td><span class="badge badge-primary">${admin.role}</span></td>
                <td>${statusBadge}</td>
                <td>${createdDate}</td>
                <td>
                    <button class="btn" style="padding: 4px 12px; font-size: 12px;" 
                            onclick="blockAdmin('${admin.id}', ${admin.status !== 'blocked'})">
                        ${admin.status === 'blocked' ? 'Unblock' : 'Block'}
                    </button>
                    <button class="btn" style="padding: 4px 12px; font-size: 12px; margin-left: 8px;" 
                            onclick="deleteAdmin('${admin.id}')">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

async function blockAdmin(adminId, block) {
    if (!confirm(`Are you sure you want to ${block ? 'block' : 'unblock'} this admin?`)) {
        return;
    }
    
    try {
        const response = await window.adminAuth.apiRequest('/admins/block', {
            method: 'PATCH',
            body: JSON.stringify({ admin_id: adminId, blocked: block })
        });
        
        if (response.ok) {
            await loadAdmins();
            alert(`Admin ${block ? 'blocked' : 'unblocked'} successfully`);
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to update admin status');
        }
    } catch (error) {
        alert('Failed to update admin status');
    }
}

async function deleteAdmin(adminId) {
    if (!confirm('Are you sure you want to delete this admin? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await window.adminAuth.apiRequest(`/admins/${adminId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadAdmins();
            alert('Admin deleted successfully');
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to delete admin');
        }
    } catch (error) {
        alert('Failed to delete admin');
    }
}

function showCreateAdminModal() {
    document.getElementById('createAdminModal').style.display = 'flex';
}

function hideCreateAdminModal() {
    document.getElementById('createAdminModal').style.display = 'none';
    document.getElementById('createAdminForm').reset();
}

async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        await window.adminAuth.logout();
    }
}

